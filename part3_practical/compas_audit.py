"""
COMPAS Recidivism Dataset Bias Audit
Using AI Fairness 360 (AIF360) to analyze racial bias in risk scores

This script analyzes the COMPAS dataset to identify racial disparities
in recidivism risk assessment scores.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import warnings
import openpyxl  # For reading Excel files
warnings.filterwarnings('ignore')

# Try to import AIF360, provide fallback if not available
try:
    from aif360.datasets import BinaryLabelDataset
    from aif360.metrics import BinaryLabelDatasetMetric, ClassificationMetric
    from aif360.algorithms.preprocessing import Reweighing
    AIF360_AVAILABLE = True
except ImportError:
    print("AIF360 not installed. Install with: pip install aif360")
    AIF360_AVAILABLE = False

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_compas_data():
    """
    Load COMPAS dataset from local file
    
    Returns:
        pd.DataFrame: COMPAS dataset
    """
    try:
        # Try loading local Excel file
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, 'DocRedacted.xlsx')
        
        if os.path.exists(data_path):
            df = pd.read_excel(data_path)
            print(f"✓ Successfully loaded COMPAS dataset from local file: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        else:
            print(f"❌ Local file not found: {data_path}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def preprocess_compas_data(df):
    """
    Preprocess COMPAS dataset for bias analysis
    
    Args:
        df (pd.DataFrame): Raw COMPAS data
        
    Returns:
        pd.DataFrame: Preprocessed data
    """
    # Filter data as done in ProPublica analysis
    df = df[
        (df['days_b_screening_arrest'] <= 30) &
        (df['days_b_screening_arrest'] >= -30) &
        (df['is_recid'] != -1) &
        (df['c_charge_degree'] != "O") &
        (df['score_text'] != 'N/A')
    ]
    
    # Select relevant columns
    columns = [
        'age', 'c_charge_degree', 'race', 'age_cat', 'score_text', 
        'sex', 'priors_count', 'days_b_screening_arrest', 
        'decile_score', 'is_recid', 'two_year_recid', 'c_jail_in', 'c_jail_out'
    ]
    
    df = df[columns].copy()
    
    # Create binary race variable (African-American vs Caucasian for primary analysis)
    df['race_binary'] = df['race'].apply(lambda x: 1 if x == 'African-American' else 0)
    
    # Binary risk score (High/Medium = 1, Low = 0)
    df['high_risk'] = df['score_text'].apply(lambda x: 1 if x in ['High', 'Medium'] else 0)
    
    # Encode categorical variables
    df['sex_binary'] = df['sex'].apply(lambda x: 1 if x == 'Male' else 0)
    df['charge_degree'] = df['c_charge_degree'].apply(lambda x: 1 if x == 'F' else 0)  # Felony = 1
    
    print(f"✓ Preprocessed data: {df.shape[0]} rows")
    print(f"  - African-American: {df[df['race'] == 'African-American'].shape[0]}")
    print(f"  - Caucasian: {df[df['race'] == 'Caucasian'].shape[0]}")
    
    return df

def calculate_basic_metrics(df):
    """
    Calculate basic fairness metrics
    
    Args:
        df (pd.DataFrame): Preprocessed COMPAS data
        
    Returns:
        dict: Dictionary of metrics
    """
    metrics = {}
    
    # Overall statistics
    total_samples = len(df)
    
    # African-American metrics
    aa_df = df[df['race'] == 'African-American']
    aa_high_risk = aa_df['high_risk'].sum()
    aa_recid = aa_df['two_year_recid'].sum()
    
    # Caucasian metrics
    cauc_df = df[df['race'] == 'Caucasian']
    cauc_high_risk = cauc_df['high_risk'].sum()
    cauc_recid = cauc_df['two_year_recid'].sum()
    
    # Calculate rates
    metrics['aa_high_risk_rate'] = aa_high_risk / len(aa_df) if len(aa_df) > 0 else 0
    metrics['cauc_high_risk_rate'] = cauc_high_risk / len(cauc_df) if len(cauc_df) > 0 else 0
    metrics['aa_recid_rate'] = aa_recid / len(aa_df) if len(aa_df) > 0 else 0
    metrics['cauc_recid_rate'] = cauc_recid / len(cauc_df) if len(cauc_df) > 0 else 0
    
    # False positive rates (predicted high risk but did not recidivate)
    aa_no_recid = aa_df[aa_df['two_year_recid'] == 0]
    aa_fp = aa_no_recid['high_risk'].sum()
    metrics['aa_fpr'] = aa_fp / len(aa_no_recid) if len(aa_no_recid) > 0 else 0
    
    cauc_no_recid = cauc_df[cauc_df['two_year_recid'] == 0]
    cauc_fp = cauc_no_recid['high_risk'].sum()
    metrics['cauc_fpr'] = cauc_fp / len(cauc_no_recid) if len(cauc_no_recid) > 0 else 0
    
    # False negative rates (predicted low risk but did recidivate)
    aa_recid_df = aa_df[aa_df['two_year_recid'] == 1]
    aa_fn = (aa_recid_df['high_risk'] == 0).sum()
    metrics['aa_fnr'] = aa_fn / len(aa_recid_df) if len(aa_recid_df) > 0 else 0
    
    cauc_recid_df = cauc_df[cauc_df['two_year_recid'] == 1]
    cauc_fn = (cauc_recid_df['high_risk'] == 0).sum()
    metrics['cauc_fnr'] = cauc_fn / len(cauc_recid_df) if len(cauc_recid_df) > 0 else 0
    
    # Disparate impact
    metrics['disparate_impact'] = metrics['aa_high_risk_rate'] / metrics['cauc_high_risk_rate'] if metrics['cauc_high_risk_rate'] > 0 else 0
    
    return metrics

def visualize_bias(df, metrics):
    """
    Create visualizations showing racial bias in COMPAS scores
    
    Args:
        df (pd.DataFrame): Preprocessed COMPAS data
        metrics (dict): Calculated fairness metrics
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('COMPAS Racial Bias Analysis', fontsize=16, fontweight='bold')
    
    # 1. Distribution of risk scores by race
    ax1 = axes[0, 0]
    race_risk = df.groupby(['race', 'score_text']).size().unstack(fill_value=0)
    race_risk_pct = race_risk.div(race_risk.sum(axis=1), axis=0) * 100
    
    races_to_plot = ['African-American', 'Caucasian']
    race_risk_pct.loc[races_to_plot].plot(kind='bar', ax=ax1, color=['green', 'orange', 'red'])
    ax1.set_title('Risk Score Distribution by Race', fontweight='bold')
    ax1.set_xlabel('Race')
    ax1.set_ylabel('Percentage (%)')
    ax1.legend(title='Risk Level')
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. High risk rates comparison
    ax2 = axes[0, 1]
    high_risk_rates = [metrics['aa_high_risk_rate'] * 100, metrics['cauc_high_risk_rate'] * 100]
    bars = ax2.bar(['African-American', 'Caucasian'], high_risk_rates, color=['#e74c3c', '#3498db'])
    ax2.set_title('High Risk Classification Rate', fontweight='bold')
    ax2.set_ylabel('Percentage (%)')
    ax2.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # 3. False Positive Rate comparison
    ax3 = axes[0, 2]
    fpr_rates = [metrics['aa_fpr'] * 100, metrics['cauc_fpr'] * 100]
    bars = ax3.bar(['African-American', 'Caucasian'], fpr_rates, color=['#e74c3c', '#3498db'])
    ax3.set_title('False Positive Rate\n(High risk but did NOT recidivate)', fontweight='bold')
    ax3.set_ylabel('Percentage (%)')
    ax3.set_ylim(0, 60)
    
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # 4. False Negative Rate comparison
    ax4 = axes[1, 0]
    fnr_rates = [metrics['aa_fnr'] * 100, metrics['cauc_fnr'] * 100]
    bars = ax4.bar(['African-American', 'Caucasian'], fnr_rates, color=['#2ecc71', '#f39c12'])
    ax4.set_title('False Negative Rate\n(Low risk but DID recidivate)', fontweight='bold')
    ax4.set_ylabel('Percentage (%)')
    ax4.set_ylim(0, 60)
    
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # 5. Decile score distribution
    ax5 = axes[1, 1]
    aa_scores = df[df['race'] == 'African-American']['decile_score']
    cauc_scores = df[df['race'] == 'Caucasian']['decile_score']
    
    ax5.hist([aa_scores, cauc_scores], bins=10, label=['African-American', 'Caucasian'], 
             alpha=0.7, color=['#e74c3c', '#3498db'])
    ax5.set_title('Decile Score Distribution', fontweight='bold')
    ax5.set_xlabel('Decile Score (1-10)')
    ax5.set_ylabel('Frequency')
    ax5.legend()
    
    # 6. Recidivism rates by risk score
    ax6 = axes[1, 2]
    
    risk_recid = df.groupby(['race', 'score_text'])['two_year_recid'].mean() * 100
    risk_recid = risk_recid.unstack()
    risk_recid.loc[races_to_plot].plot(kind='bar', ax=ax6, color=['green', 'orange', 'red'])
    ax6.set_title('Actual Recidivism Rate by Risk Score', fontweight='bold')
    ax6.set_xlabel('Race')
    ax6.set_ylabel('Recidivism Rate (%)')
    ax6.legend(title='Risk Level')
    ax6.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('compas_bias_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Visualization saved as 'compas_bias_analysis.png'")
    plt.show()

def print_metrics_report(metrics):
    """
    Print a formatted report of fairness metrics
    
    Args:
        metrics (dict): Calculated fairness metrics
    """
    print("\n" + "="*70)
    print("COMPAS BIAS ANALYSIS - KEY FINDINGS")
    print("="*70)
    
    print("\n1. HIGH RISK CLASSIFICATION RATES:")
    print(f"   African-American:  {metrics['aa_high_risk_rate']*100:.2f}%")
    print(f"   Caucasian:         {metrics['cauc_high_risk_rate']*100:.2f}%")
    print(f"   Disparity:         {(metrics['aa_high_risk_rate'] - metrics['cauc_high_risk_rate'])*100:.2f} percentage points")
    
    print("\n2. FALSE POSITIVE RATES (Predicted high risk, did NOT recidivate):")
    print(f"   African-American:  {metrics['aa_fpr']*100:.2f}%")
    print(f"   Caucasian:         {metrics['cauc_fpr']*100:.2f}%")
    print(f"   Disparity:         {(metrics['aa_fpr'] - metrics['cauc_fpr'])*100:.2f} percentage points")
    print(f"   ⚠ African-Americans are {metrics['aa_fpr']/metrics['cauc_fpr']:.2f}x more likely to be false positives")
    
    print("\n3. FALSE NEGATIVE RATES (Predicted low risk, DID recidivate):")
    print(f"   African-American:  {metrics['aa_fnr']*100:.2f}%")
    print(f"   Caucasian:         {metrics['cauc_fnr']*100:.2f}%")
    print(f"   Disparity:         {(metrics['aa_fnr'] - metrics['cauc_fnr'])*100:.2f} percentage points")
    print(f"   ⚠ Caucasians are {metrics['cauc_fnr']/metrics['aa_fnr']:.2f}x more likely to be false negatives")
    
    print("\n4. ACTUAL RECIDIVISM RATES:")
    print(f"   African-American:  {metrics['aa_recid_rate']*100:.2f}%")
    print(f"   Caucasian:         {metrics['cauc_recid_rate']*100:.2f}%")
    
    print("\n5. DISPARATE IMPACT RATIO:")
    print(f"   {metrics['disparate_impact']:.3f}")
    if metrics['disparate_impact'] < 0.8:
        print("   ⚠ FAILS 80% rule (indicates adverse impact)")
    else:
        print("   ✓ Passes 80% rule")
    
    print("\n" + "="*70)

def generate_remediation_recommendations():
    """
    Generate recommendations for addressing bias
    """
    recommendations = """
REMEDIATION RECOMMENDATIONS:

1. DATA COLLECTION & TRAINING:
   - Audit training data for racial representation and historical bias
   - Ensure balanced representation across racial groups
   - Remove features that are proxies for race (e.g., zip codes in segregated areas)
   - Include socioeconomic factors that explain behavior better than race

2. MODEL ADJUSTMENTS:
   - Implement fairness constraints during model training (e.g., equalized odds)
   - Use reweighing or adversarial debiasing techniques
   - Consider separate thresholds for different groups to achieve equal FPR/FNR
   - Regular recalibration with recent data

3. PROCESS IMPROVEMENTS:
   - Mandatory human review of all risk assessments
   - Provide judges with confidence intervals and uncertainty measures
   - Transparency: explain which factors contributed to each score
   - Allow defendants to challenge and correct factual errors in their data

4. MONITORING & ACCOUNTABILITY:
   - Continuous monitoring of disparate impact across racial groups
   - Quarterly bias audits with public reporting
   - Track downstream outcomes (bail decisions, sentencing) by race
   - Independent oversight board with community representation

5. POLICY REFORMS:
   - Limit use of risk scores to specific decisions (e.g., not for sentencing)
   - Provide right to algorithmic explanation
   - Create appeals process for those harmed by false positives
   - Consider moratorium until bias is adequately addressed
"""
    return recommendations

def main():
    """
    Main execution function
    """
    print("COMPAS RECIDIVISM DATASET BIAS AUDIT")
    print("="*70)
    
    # Load data
    print("\n1. Loading COMPAS dataset...")
    df = load_compas_data()
    
    if df is None:
        print("❌ Failed to load data. Exiting.")
        return
    
    # Preprocess
    print("\n2. Preprocessing data...")
    df = preprocess_compas_data(df)
    
    # Calculate metrics
    print("\n3. Calculating fairness metrics...")
    metrics = calculate_basic_metrics(df)
    
    # Print report
    print_metrics_report(metrics)
    
    # Visualize
    print("\n4. Generating visualizations...")
    visualize_bias(df, metrics)
    
    # Recommendations
    print("\n5. Remediation Recommendations:")
    print(generate_remediation_recommendations())
    
    print("\n✓ Analysis complete!")

if __name__ == "__main__":
    main()

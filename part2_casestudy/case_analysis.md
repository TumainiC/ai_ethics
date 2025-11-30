# Part 2: Case Study Analysis

## Case 1: Biased Hiring Tool - Amazon's AI Recruiting System

### Background
Amazon's AI recruiting tool was designed to automate resume screening but was discovered to systematically penalize female candidates, particularly for technical positions.

### 1. Source of Bias

The primary source of bias stemmed from the **training data**:

- **Historical Data Bias**: The model was trained on resumes submitted to Amazon over a 10-year period, predominantly from male candidates. Since the tech industry historically has had male-dominated hiring patterns, the AI learned to favor patterns associated with male resumes.

- **Feature Engineering Issues**: The model identified gendered language patterns as predictive features. For example, resumes containing words like "women's" (e.g., "women's chess club captain") were penalized, and the system downgraded graduates from all-women's colleges.

- **Proxy Variables**: The model inadvertently used gender as a proxy through correlated features such as sports teams, clubs, and educational institutions that are gender-associated.

### 2. Three Fixes to Make the Tool Fairer

**Fix 1: Diverse and Balanced Training Data**
- Reconstruct the training dataset to include equal representation of successful male and female candidates
- Use synthetic data augmentation to balance gender representation
- Include successful candidates from diverse backgrounds and institutions
- Remove historical hiring data that reflects past discriminatory practices

**Fix 2: Fairness-Aware Machine Learning Techniques**
- Implement adversarial debiasing where a secondary model attempts to predict gender from the hiring model's internal representations, and the primary model is trained to prevent this
- Apply reweighing techniques to give more importance to underrepresented groups during training
- Use fairness constraints during optimization (e.g., demographic parity or equalized odds constraints)
- Remove explicitly gendered terms and gender-proxy features from the feature set

**Fix 3: Human-in-the-Loop Validation and Ongoing Monitoring**
- Implement mandatory human review for all AI recommendations, especially for borderline cases
- Create diverse hiring panels to review AI-flagged candidates
- Establish regular bias audits with gender-disaggregated performance metrics
- Set up feedback loops where human recruiters can flag biased decisions to retrain the model
- Implement explainability tools to understand why candidates are ranked certain ways

### 3. Metrics to Evaluate Fairness Post-Correction

**Demographic Parity Metrics:**
- **Selection Rate Parity**: The percentage of male vs. female candidates recommended should be proportional to the qualified applicant pool
  - Formula: P(Ŷ=1|Gender=Male) ≈ P(Ŷ=1|Gender=Female)
  
**Equalized Odds Metrics:**
- **True Positive Rate (TPR) Parity**: The rate at which qualified male and female candidates are correctly identified should be equal
  - TPR_male ≈ TPR_female
- **False Positive Rate (FPR) Parity**: The rate at which unqualified candidates are incorrectly recommended should be equal across genders
  - FPR_male ≈ FPR_female

**Predictive Parity Metrics:**
- **Positive Predictive Value (PPV) Parity**: Among candidates recommended by the AI, the success rate should be equal across genders
  - PPV_male ≈ PPV_female

**Calibration Metrics:**
- **Calibration Across Groups**: For candidates assigned similar scores, actual success rates should be similar regardless of gender
  - For score S: P(Success|Score=S, Gender=Male) ≈ P(Success|Score=S, Gender=Female)

**Additional Fairness Metrics:**
- **Disparate Impact Ratio**: Ratio of selection rates between protected and unprotected groups should be ≥ 0.8 (80% rule)
  - DIR = (Female Selection Rate) / (Male Selection Rate) should be between 0.8 and 1.25
- **Statistical Parity Difference**: Absolute difference in selection rates should be minimal (ideally < 0.1)

**Process Metrics:**
- Time-to-hire equity across gender groups
- Interview invitation rates by gender
- Offer acceptance rates by gender
- Long-term success metrics (performance reviews, retention) by gender

---

## Case 2: Facial Recognition in Policing

### Background
Facial recognition systems deployed in law enforcement have been shown to misidentify minorities, particularly Black and Asian individuals, at significantly higher rates than white individuals.

### 1. Ethical Risks

**Wrongful Arrests and Criminalization**
- **False Positives Leading to Wrongful Detention**: Higher misidentification rates for minorities mean innocent people are more likely to be wrongly arrested, detained, and potentially prosecuted
- **Compounding Bias**: These systems can amplify existing racial biases in policing, leading to disproportionate targeting of minority communities
- **Psychological and Social Harm**: Wrongful arrests cause trauma, job loss, reputational damage, and erosion of trust in law enforcement
- **Due Process Violations**: Individuals may be detained based on algorithmic decisions without proper probable cause

**Privacy Violations**
- **Mass Surveillance**: Facial recognition enables warrantless, continuous surveillance of public spaces, disproportionately affecting minority neighborhoods that are often over-policed
- **Chilling Effects**: Knowledge of constant monitoring can suppress freedom of movement, assembly, and expression, particularly in communities already marginalized
- **Data Collection Without Consent**: Individuals' biometric data is collected and stored without knowledge or consent
- **Scope Creep**: Data collected for one purpose (e.g., identifying suspects) can be repurposed for broader surveillance

**Erosion of Civil Liberties**
- **Presumption of Guilt**: Being flagged by facial recognition can create a presumption of guilt rather than innocence
- **Lack of Transparency**: Individuals often don't know when they've been scanned or why they were flagged
- **Unequal Protection Under Law**: Higher error rates for minorities mean unequal application of surveillance and enforcement

**Reinforcement of Systemic Discrimination**
- **Feedback Loops**: If minorities are arrested more due to false positives, this creates more "criminal records" that justify further surveillance
- **Historical Bias Amplification**: Training data often reflects historical patterns of discriminatory policing
- **Resource Misallocation**: Over-policing of minority communities based on flawed data perpetuates inequity

**Accountability Gaps**
- **Diffusion of Responsibility**: Errors are blamed on "the algorithm," making it difficult to hold anyone accountable
- **Opacity**: Proprietary systems lack transparency, preventing independent audits
- **Limited Recourse**: Victims of misidentification often have limited legal remedies

### 2. Policies for Responsible Deployment

**Pre-Deployment Requirements**

**Policy 1: Mandatory Bias Testing and Certification**
- Require independent, third-party testing of facial recognition systems before deployment
- Systems must demonstrate accuracy rates above 99% across all demographic groups (race, gender, age)
- Publish disaggregated performance metrics publicly
- Require annual re-certification with updated test data

**Policy 2: Strict Use Case Limitations**
- Prohibit use of facial recognition for:
  - Mass surveillance in public spaces
  - Identification at protests or political gatherings
  - Real-time identification without prior warrant
- Limit use to specific, serious crimes (e.g., violent felonies, missing persons)
- Require judicial warrant before deployment in most cases

**Deployment Safeguards**

**Policy 3: Human Review and Verification Requirements**
- Mandate that facial recognition can NEVER be the sole basis for arrest or detention
- Require human expert review of all matches before any law enforcement action
- Implement minimum confidence thresholds (e.g., 95%+) before human review
- Require corroborating evidence beyond facial recognition match

**Policy 4: Transparency and Explainability Standards**
- Require open-source algorithms or source code escrow for judicial review
- Law enforcement must disclose use of facial recognition in arrest affidavits
- Defendants must receive all facial recognition data and match scores
- Public registry of when and where systems are deployed

**Accountability Mechanisms**

**Policy 5: Data Protection and Privacy Safeguards**
- Limit database sources to criminal mugshots only (no DMV, social media, or commercial databases)
- Mandatory data minimization: delete scans that don't match within 24 hours
- Prohibition on sharing data with third parties or other agencies without court order
- Right to know if you've been scanned and matched

**Policy 6: Community Oversight and Consent**
- Require community input before deployment through public hearings
- Create civilian oversight boards with subpoena power to audit usage
- Allow communities to opt-out of facial recognition deployment
- Regular public reporting on usage statistics and error rates

**Policy 7: Legal Liability and Redress**
- Hold vendors liable for discriminatory performance through contract terms
- Create civil cause of action for victims of misidentification
- Automatic expungement of records for false positive arrests
- Compensation fund for victims of wrongful detention

**Policy 8: Training and Expertise Requirements**
- Require specialized training for officers using facial recognition
- Training must include bias awareness and system limitations
- Designate certified specialists for system operation
- Document all usage with justification and outcomes

**Policy 9: Sunset Provisions and Ongoing Evaluation**
- Implement 2-year sunset clauses requiring re-authorization
- Mandatory annual third-party audits of deployment outcomes
- Disaggregated analysis of impact on different demographic groups
- Authority to suspend deployment if disparate impact is identified

**Policy 10: Alternative Investigation Methods**
- Require documentation that traditional investigative methods were considered
- Invest in less invasive alternatives (e.g., tip lines, witness interviews)
- Prioritize community policing over technological surveillance

**International Best Practices**
- Study and adopt successful frameworks from jurisdictions with protective regulations
- Consider moratorium models (like San Francisco, Boston) until technology improves
- Align with EU's proposed AI Act classifications and risk-based approach

---

## Conclusion

Both case studies demonstrate that AI systems can perpetuate and amplify existing societal biases if not carefully designed, tested, and monitored. The Amazon hiring tool shows how historical data can encode discrimination, while facial recognition in policing reveals how technical limitations can have serious civil liberties implications. 

Key lessons:
1. **Data quality matters**: Biased input data leads to biased outputs
2. **Testing must be comprehensive**: Evaluate performance across all demographic groups
3. **Human oversight is essential**: AI should augment, not replace, human judgment
4. **Transparency enables accountability**: Stakeholders need visibility into how systems work
5. **Continuous monitoring is required**: Bias can emerge or evolve over time

Responsible AI deployment requires proactive measures throughout the entire lifecycle—from design and training through deployment and ongoing evaluation.

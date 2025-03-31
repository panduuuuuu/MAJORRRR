import matplotlib
matplotlib.use('Agg')
import os
import numpy as np
import pandas as pd
import statistics
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import openai

# Set your OpenAI API key
openai.api_key = "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"



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

DATA_PATH = "dataset/Train.csv"
data = pd.read_csv(DATA_PATH).dropna(axis=1)

# Encode target labels
encoder = LabelEncoder()
data["prognosis"] = encoder.fit_transform(data["prognosis"])

X = data.iloc[:, :-1]
y = data.iloc[:, -1]

# Define columns directly in app.py
columns = list(X.columns)

# Train models
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=24)
svm_model = SVC()
bn_model = GaussianNB()
rf_model = RandomForestClassifier(random_state=18)

svm_model.fit(X_train, y_train)
bn_model.fit(X_train, y_train)
rf_model.fit(X_train, y_train)

# Compute model accuracies
svm_accuracy = round(accuracy_score(y_test, svm_model.predict(X_test)) * 100, 2)
bn_accuracy = round(accuracy_score(y_test, bn_model.predict(X_test)) * 100, 2)
rf_accuracy = round(accuracy_score(y_test, rf_model.predict(X_test)) * 100, 2)

# Load symptom names
symptoms = X.columns.values
symptom_index = {symptom: index for index, symptom in enumerate(symptoms)}

# Disease treatments
disease_treatment = { 
                       "Fungal infection": "Use antifungal creams and keep the affected area dry.",
 "Allergy": "Take antihistamines and avoid allergens.",
 "GERD": "Avoid spicy foods, eat smaller meals, and take antacids.",
 "Chronic cholestasis": "Consult a specialist for bile acid sequestrants and dietary changes.",
 "Drug Reaction": "Discontinue the drug and seek immediate medical attention.",
 "Peptic ulcer disease": "Avoid NSAIDs, take proton pump inhibitors, and manage stress.",
 "AIDS": "Follow antiretroviral therapy as prescribed by a doctor.",
 "Diabetes": "Maintain a balanced diet, exercise regularly, and monitor blood sugar levels.",
 "Gastroenteritis": "Stay hydrated, take probiotics, and rest.",
 "Bronchial Asthma": "Use inhalers and avoid triggers like dust and pollen.",
 "Hypertension": "Reduce salt intake, exercise regularly, and manage stress.",
 "Migraine": "Take pain relievers, avoid triggers, and practice relaxation techniques.",
 "Cervical spondylosis": "Do neck exercises, maintain good posture, and use pain relievers.",
 "Paralysis (brain hemorrhage)": "Seek immediate medical attention and undergo rehabilitation.",
 "Jaundice": "Rest, drink plenty of fluids, and follow a healthy diet.",
 "Malaria": "Take antimalarial medications and use mosquito protection.",
 "Chicken pox": "Rest, take antihistamines, and apply calamine lotion for itch relief.",
 "Dengue": "Stay hydrated, monitor platelet count, and take pain relievers as needed.",
 "Typhoid": "Follow a course of antibiotics and maintain proper hydration.",
 "Hepatitis A": "Rest, maintain hygiene, and avoid alcohol.",
 "Hepatitis B": "Follow antiviral therapy and avoid alcohol.",
 "Hepatitis C": "Consult a doctor for antiviral medication and regular monitoring.",
 "Hepatitis D": "Follow a hepatitis B management plan and avoid alcohol.",
 "Hepatitis E": "Rest, stay hydrated, and avoid alcohol.",
 "Alcoholic hepatitis": "Avoid alcohol, take prescribed medications, and follow a healthy diet.",
 "Tuberculosis": "Follow a full course of antibiotics and maintain good nutrition.",
 "Common Cold": "Rest, drink warm fluids, and take over-the-counter cold medications.",
 "Pneumonia": "Take prescribed antibiotics and get plenty of rest.",
 "Dimorphic hemorrhoids (piles)": "Increase fiber intake, stay hydrated, and use medicated creams.",
 "Heart attack": "Seek emergency medical help and follow a cardiac rehabilitation program.",
 "Varicose veins": "Exercise, wear compression stockings, and avoid standing for long periods.",
 "Hypothyroidism": "Take thyroid hormone replacement therapy as prescribed.",
 "Hyperthyroidism": "Follow doctor’s recommendations for medication or radioactive iodine therapy.",
 "Hypoglycemia": "Consume fast-acting sugar and monitor blood sugar levels regularly.",
 "Osteoarthritis": "Engage in low-impact exercises and take pain relievers if needed.",
 "Arthritis": "Take anti-inflammatory medications and maintain an active lifestyle.",
 "(Vertigo) Paroxysmal Positional Vertigo": "Avoid sudden head movements and follow vestibular rehabilitation therapy.",
 "Acne": "Use medicated cleansers and apply topical treatments as needed.",
 "Urinary tract infection": "Drink plenty of fluids, urinate frequently, and take prescribed antibiotics.",
 "Psoriasis": "Use moisturizing creams, take medicated baths, and avoid stress.",
 "Impetigo": "Apply antibiotic creams and maintain good hygiene."}  # Keeping existing treatments unchanged

def generate_confusion_matrix(model_name, model, X_symptom_filtered, y_symptom_filtered, filename):
    if len(y_symptom_filtered) == 0:
        return None
    
    y_pred = model.predict(X_symptom_filtered)
    unique_labels = np.unique(np.concatenate((y_symptom_filtered, y_pred)))
    
    conf_matrix = confusion_matrix(y_symptom_filtered, y_pred, labels=unique_labels)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap='Blues', xticklabels=encoder.inverse_transform(unique_labels), yticklabels=encoder.inverse_transform(unique_labels))
    plt.title(f'Confusion Matrix for {model_name}')
    plt.xlabel('Predicted Labels')
    plt.ylabel('Actual Labels')
    
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    return filename

def predict_disease(symptom_list):
    input_data = [0] * len(symptom_index)
    for symptom in symptom_list:
        if symptom in symptom_index:
            input_data[symptom_index[symptom]] = 1

    input_df = pd.DataFrame([input_data], columns=symptoms)
    rf_prediction = encoder.classes_[rf_model.predict(input_df)[0]]
    bn_prediction = encoder.classes_[bn_model.predict(input_df)[0]]
    svm_prediction = encoder.classes_[svm_model.predict(input_df)[0]]

    try:
        final_prediction = statistics.mode([rf_prediction, bn_prediction, svm_prediction])
    except statistics.StatisticsError:
        final_prediction = rf_prediction  

    treatment = disease_treatment.get(final_prediction, "No specific treatment available")
    
    return {
        "Random Forest Prediction": rf_prediction,
        "Naive Bayes Prediction": bn_prediction,
        "SVM Prediction": svm_prediction,
        "Final Prediction": final_prediction,
        "Treatment": treatment
    }

@app.route("/chat", methods=["POST"])
def chatbot():
    data = request.json
    user_message = data.get("message", "")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": (
                    "You are MedScope AI Chatbot, an assistant for the MedScope health prediction website. "
                    "MedScope provides disease prediction based on symptoms, severity analysis, and risk assessment. "
                    "Users can visualize symptoms, analyze risks, and chat with you for help. "
                    "Answer questions related to MedScope's features and health-related queries."
                )},
                {"role": "user", "content": user_message}
            ]
        )
        bot_reply = response["choices"][0]["message"]["content"]
        return jsonify({"response": bot_reply})
    
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

@app.route("/")
def home():
    symptoms_list = X.columns if isinstance(X, pd.DataFrame) else []
    return render_template("home.html", symptoms=symptoms_list)

@app.route("/index")
def index():
    symptoms_list = X.columns if isinstance(X, pd.DataFrame) else []
    return render_template("index.html", symptoms=symptoms_list)
@app.route('/symptom_visualization')
def symptom_visualization():
    return render_template('symptom_visualization.html')
@app.route('/disease_severity', methods=['GET', 'POST'])
def disease_severity():
    if request.method == 'POST':
        age = int(request.form.get('age'))
        selected_symptoms = request.form.getlist('symptoms')

        # Calculate severity score based on age and symptoms
        severity_score = len(selected_symptoms) * (1 + age / 100)
        severity = "Low" if severity_score < 5 else "Moderate" if severity_score < 10 else "High"

        # Suggested actions based on severity
        if severity == "High":
            suggested_actions = "Immediate medical attention is recommended."
        elif severity == "Moderate":
            suggested_actions = "Consult a healthcare provider and monitor symptoms."
        else:
            suggested_actions = "Maintain a healthy lifestyle and monitor for any changes."

        # Generate severity chart
        plt.figure(figsize=(6, 4))
        plt.bar(['Severity Score'], [severity_score], color='orange' if severity == "High" else 'yellow' if severity == "Moderate" else 'green')
        plt.title(f'Severity Level: {severity}')
        plt.ylim(0, 15)

        chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'severity_chart.png')
        plt.savefig(chart_path)
        plt.close()

        return render_template('disease_severity.html', age=age, severity=severity, severity_score=severity_score, severity_visualization=f'/{chart_path}', suggested_actions=suggested_actions, symptoms=symptoms)

    symptoms_list = X.columns if isinstance(X, pd.DataFrame) else []
    return render_template('disease_severity.html', symptoms=symptoms_list)



@app.route("/predict", methods=["POST"])
def predict():
    name = request.form.get("name")
    age = request.form.get("age")
    selected_symptoms = request.form.getlist("symptoms")
    selected_symptoms = [s for s in selected_symptoms if s in symptom_index]  # Filter invalid symptoms

    results = predict_disease(selected_symptoms)

    # Filter test data based on selected symptoms
    relevant_indices = X_test[selected_symptoms].sum(axis=1) > 0
    X_symptom_filtered = X_test[relevant_indices]
    y_symptom_filtered = y_test[relevant_indices]

    rf_cm = generate_confusion_matrix("Random Forest", rf_model, X_symptom_filtered, y_symptom_filtered, "rf_cm.png")
    bn_cm = generate_confusion_matrix("Naive Bayes", bn_model, X_symptom_filtered, y_symptom_filtered, "nb_cm.png")
    svm_cm = generate_confusion_matrix("SVM", svm_model, X_symptom_filtered, y_symptom_filtered, "svm_cm.png")

    return render_template(
        "results.html", name=name, age=age, results=results,
        svm_accuracy=svm_accuracy, bn_accuracy=bn_accuracy, rf_accuracy=rf_accuracy,
        rf_cm=rf_cm, bn_cm=bn_cm, svm_cm=svm_cm
    )

if __name__ == "__main__":
    app.run(debug=True)

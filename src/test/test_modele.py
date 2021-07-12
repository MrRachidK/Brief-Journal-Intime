import src.utils.functions as script
import joblib
import pytest

model = joblib.load("/home/apprenant/Documents/Brief-Journal-Intime/src/models/regression_logistique_model.sav")
vectorizer = joblib.load("/home/apprenant/Documents/Brief-Journal-Intime/src/models/regression_logistique_vectorizer.joblib")

class TestModele:

    # Test if the predict method returns the right type, namely a ndarray
    def test_model(self):
        preprocessed_message = script.preprocessor("I am happy")
        vectorized_message = vectorizer.transform([preprocessed_message])
        emotion = model[0].predict(vectorized_message)
        assert type(emotion).__name__ == "ndarray"

    # Test if the model predicts the right emotion
    def test_predict_emotion(self):
        prediction, probability = script.predict_emotion("I am the happiest person in the world", vectorizer, model)
        assert prediction == "emotion positive" and type(probability).__name__ == "ndarray"

    # Test if an empty message raises an error 
    @pytest.fixture
    def test_predict_emotion(self):
        message = ""
        with pytest.raises(ValueError):
            script.predict_emotion(message, vectorizer, model)
        
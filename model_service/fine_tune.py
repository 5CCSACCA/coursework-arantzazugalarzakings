import mlflow
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np


def fine_tune_model():
    # Initialize MLflow
    mlflow.set_tracking_uri("file:///tmp/mlruns")  # Adjust to your MLflow tracking URI
    mlflow.set_experiment("Emotion Detection Fine-Tuning")

    # Load dataset
    dataset = load_dataset("emotion")

    # Preprocess the data
    def preprocess_function(examples):
        tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
        return tokenizer(examples["text"], truncation=True, padding=True, max_length=128)

    tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
    encoded_dataset = dataset.map(preprocess_function, batched=True)

    # Prepare data splits
    train_dataset = encoded_dataset["train"].shuffle(seed=42).select(range(1000))  # Subset for demonstration
    test_dataset = encoded_dataset["test"].shuffle(seed=42).select(range(200))    # Subset for demonstration

    # Load the model
    model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

    # Metric function
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        preds = np.argmax(predictions, axis=1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted")
        acc = accuracy_score(labels, preds)
        return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

    # Fine-tuning parameters
    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",  # Ensure evaluation happens at the end of each epoch
        save_strategy="epoch",        # Align save strategy with evaluation strategy
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=1,           # Minimal epochs for demonstration
        logging_dir="./logs",
        logging_steps=10,
        load_best_model_at_end=True,  # Load the best model at the end of training
        metric_for_best_model="accuracy",
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # Fine-tune and log with MLflow
    with mlflow.start_run(run_name="Fine-Tuning Emotion Model"):
        # Log training parameters
        mlflow.log_param("learning_rate", training_args.learning_rate)
        mlflow.log_param("epochs", training_args.num_train_epochs)
        mlflow.log_param("batch_size", training_args.per_device_train_batch_size)

        # Fine-tune the model
        trainer.train()

        # Log metrics
        metrics = trainer.evaluate()
        for key, value in metrics.items():
            mlflow.log_metric(key, value)

        # Save the model to MLflow
        model_dir = "./mlflow_model"
        trainer.save_model(model_dir)
        mlflow.log_artifacts(model_dir, artifact_path="model")

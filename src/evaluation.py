import json
from pathlib import Path
from datasets import Dataset
from ragas.metrics import faithfulness, answer_relevancy, context_recall
from ragas import evaluate

def load_test_dataset(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def collect_rag_outputs(test_data: list[dict]) -> list[dict]:
    rows = []
    for item in test_data:
        answer, contexts = get_answer_and_contexts(item["question"])
        row = {
            "question": item["question"],
            "answer": answer,
            "contexts": contexts,
            "ground_truth": item["ground_truth"]
        }
        rows.append(row)
    return rows

def run_evaluation():
    test_data = load_test_dataset(Path("eval/test_questions.json"))
    rag_outputs = collect_rag_outputs(test_data)
    dataset = Dataset.from_list(rag_outputs)
    print(evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_recall]))


if __name__ == "__main__":
    run_evaluation()

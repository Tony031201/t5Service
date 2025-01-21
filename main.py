from transformers import T5Tokenizer, T5ForConditionalGeneration
from t5base_context import context as t5_context
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class QuestionRequest(BaseModel):
    question: str

# 创建 FastAPI 应用
app = FastAPI()

# question = 'How much time I need to wait for the soup when I try to heat them?'

model_name = "t5-base"
tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
model = T5ForConditionalGeneration.from_pretrained(model_name)

@app.get('/')
def home():
    return "Hello from your Railway-deployed Python service!"

@app.post("/predict/")
def pred(request: QuestionRequest):
    try:
        print('enter predict function')
        question = request.question
        print(f"Received question: {question}")
        # 输入与生成
        input_text = f"question: {question} context: {t5_context}"
        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        outputs = model.generate(
            inputs["input_ids"],
            max_length=500,
            min_length=50,
            num_beams=5,
            repetition_penalty=1.2
        )
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"answer": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0', port=5000)
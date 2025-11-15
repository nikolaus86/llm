# model_tester.py
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

class ModelTester:
    def __init__(self):
        self.results = []
        self.dialogs = {}
        
    def test_model(self, model_name, system_prompt, dialog_scenario):
        """Тестирование конкретной модели на сценарии"""
        
        try:
            # Для демонстрации используем pipeline
            # В реальном проекте здесь будет код для разных моделей
            pipe = pipeline(
                "text-generation",
                model="Qwen/Qwen-2.5-1.5B",  # Пример легковесной модели
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            conversation = []
            for i, turn in enumerate(dialog_scenario):
                if turn["role"] == "user":
                    # Формируем промпт с историей диалога
                    messages = [
                        {"role": "system", "content": system_prompt},
                        *conversation,
                        {"role": "user", "content": turn["content"]}
                    ]
                    
                    prompt = self.format_prompt(messages)
                    response = pipe(prompt, max_new_tokens=256)[0]['generated_text']
                    
                    # Извлекаем ответ модели
                    model_response = self.extract_response(response, prompt)
                    
                    # Сохраняем в историю
                    conversation.append({"role": "user", "content": turn["content"]})
                    conversation.append({"role": "assistant", "content": model_response})
                    
                    # Сохраняем результат
                    self.save_turn_result(
                        dialog_id=f"dialog_{model_name.replace('-', '_')}",
                        turn_number=i//2 + 1,
                        role="assistant",
                        content=turn["content"],
                        model_response=model_response,
                        rating=7  # Пример оценки
                    )
            
            return True
            
        except Exception as e:
            print(f"Ошибка тестирования {model_name}: {e}")
            return False
    
    def format_prompt(self, messages):
        """Форматирование промпта для модели"""
        formatted = ""
        for msg in messages:
            if msg["role"] == "system":
                formatted += f"<|system|>\n{msg['content']}\n<|end|>\n"
            elif msg["role"] == "user":
                formatted += f"<|user|>\n{msg['content']}\n<|end|>\n"
            else:
                formatted += f"<|assistant|>\n{msg['content']}\n<|end|>\n"
        formatted += "<|assistant|>\n"
        return formatted
    
    def extract_response(self, full_text, prompt):
        """Извлечение ответа модели из полного текста"""
        if prompt in full_text:
            return full_text.replace(prompt, "").strip()
        return full_text.strip()
    
    def save_turn_result(self, dialog_id, turn_number, role, content, model_response, rating):
        """Сохранение результата одного хода диалога"""
        
        if dialog_id not in self.dialogs:
            self.dialogs[dialog_id] = []
            
        self.dialogs[dialog_id].append({
            "turn_number": turn_number,
            "role": role,
            "content": content,
            "model_response": model_response,
            "rating": rating
        })
    
    def generate_reports(self):
        """Генерация всех отчетов"""
        
        # Основной отчет
        main_report = []
        for model in education_ai.models_to_test:
            for scenario in education_ai.scenarios[:2]:  # Тестируем на 2 сценариях для демо
                main_report.append({
                    "model_name": model["name"],
                    "model_parameters": model["params"],
                    "lecture_title": scenario["title"],
                    "lecture_topic": scenario["topic"],
                    "system_prompt_id": "prompt_lecture_001",
                    "dialog_id": f"dialog_{model['name'].replace('-', '_')}_{scenario['id']}",
                    "overall_rating": 8,  # Пример оценки
                    "evaluation_notes": "Модель адекватно отвечает на вопросы по теме"
                })
        
        # Сохраняем основной отчет
        pd.DataFrame(main_report).to_csv("main_report.csv", index=False)
        
        # Сохраняем системные промпты
        prompts_df = pd.DataFrame(prompts_manager.prompts.values())
        prompts_df.to_csv("system_prompts.csv", index=False)
        
        # Сохраняем диалоги
        for dialog_id, turns in self.dialogs.items():
            pd.DataFrame(turns).to_csv(f"{dialog_id}.csv", index=False)
        
        print("Отчеты успешно сгенерированы!")
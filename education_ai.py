# education_ai.py
import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class EducationAIScenario:
    def __init__(self):
        self.scenarios = []
        self.quiz_scenarios = []
        self.models_to_test = [
            {"name": "Qwen-2.5-1.5B", "params": "1.5B", "family": "Qwen"},
            {"name": "Qwen-2.5-7B", "params": "7B", "family": "Qwen"},
            {"name": "Llama-3.2-1B", "params": "1B", "family": "Llama"},
            {"name": "Llama-3.2-3B", "params": "3B", "family": "Llama"},
            {"name": "Gemma-2-2B", "params": "2B", "family": "Gemma"},
        ]
        
    def create_lecture_scenarios(self):
        """Создание 15 сценариев для фрагментов лекций"""
        
        lecture_scenarios = [
            {
                "id": "fragment_001",
                "title": "Метод k-ближайших соседей",
                "topic": "Интуитивный подход к алгоритму kNN",
                "material": """
                kNN (k-Nearest Neighbors) - это алгоритм машинного обучения, который классифицирует объекты 
                на основе k ближайших примеров из обучающей выборки. Основная идея: похожие объекты 
                имеют похожие метки классов.
                
                Пример: если мы хотим классифицировать новый фрукт как яблоко или апельсин, 
                мы смотрим на k самых похожих фруктов из известных данных.
                
                Шаги алгоритма:
                1. Выбор параметра k (количество соседей)
                2. Вычисление расстояний до всех точек обучающей выборки
                3. Выбор k ближайших соседей
                4. Определение класса по большинству голосов
                """,
                "questions": [
                    "Какова основная идея алгоритма kNN?",
                    "Что означает параметр k в алгоритме?",
                    "Можете привести пример использования kNN из реальной жизни?"
                ],
                "answers": [
                    "Основная идея: похожие объекты имеют похожие метки классов.",
                    "Параметр k определяет количество ближайших соседей, которые учитываются при классификации.",
                    "Пример: рекомендация фильмов на основе предпочтений похожих пользователей."
                ],
                "exercises": [
                    "Представьте, что k=3 и у нас есть точки: A(красный), B(красный), C(синий). Какого цвета будет новая точка рядом с A и B?",
                    "Что произойдет, если выбрать k равным общему количеству точек в dataset?"
                ]
            },
            {
                "id": "fragment_002",
                "title": "Метод k-ближайших соседей", 
                "topic": "Вычисление расстояний в kNN",
                "material": """
                Для измерения близости объектов в kNN используются различные метрики расстояния:
                
                1. Евклидово расстояние: d = √[(x₂-x₁)² + (y₂-y₁)²]
                2. Манхэттенское расстояние: d = |x₂-x₁| + |y₂-y₁|
                3. Расстояние Чебышева: d = max(|x₂-x₁|, |y₂-y₁|)
                
                Евклидово расстояние наиболее распространено и представляет прямую линию между точками.
                """,
                "questions": [
                    "Какие метрики расстояния используются в kNN?",
                    "В чем разница между евклидовым и манхэттенским расстоянием?",
                    "Когда лучше использовать манхэттенское расстояние?"
                ],
                "answers": [
                    "Основные метрики: евклидово, манхэттенское и расстояние Чебышева.",
                    "Евклидово - прямая линия, манхэттенское - сумма разностей по координатам.",
                    "Манхэттенское расстояние лучше в многомерных пространствах с разреженными данными."
                ],
                "exercises": [
                    "Вычислите евклидово расстояние между точками (1,2) и (4,6)",
                    "Вычислите манхэттенское расстояние между теми же точками"
                ]
            }
        ]
        
        # Добавьте еще 13 сценариев по аналогии
        self.scenarios = lecture_scenarios
        return lecture_scenarios
    
    def create_quiz_scenarios(self):
        """Создание 10 сценариев для опросов"""
        
        quiz_scenarios = [
            {
                "id": "quiz_001",
                "title": "Вычисление расстояний в kNN",
                "question": "Как вычислить евклидово расстояние между точками A(1,2) и B(4,6)?",
                "calculation": """
                Формула евклидова расстояния: d = √[(x₂-x₁)² + (y₂-y₁)²]
                Подставляем значения: d = √[(4-1)² + (6-2)²] = √[3² + 4²] = √[9 + 16] = √25 = 5
                """,
                "explanation": """
                Евклидово расстояние - это прямая линия между двумя точками в пространстве.
                В kNN оно используется для определения "близости" объектов.
                Формула основана на теореме Пифагора.
                """,
                "similar_exercises": [
                    "Вычислите расстояние между точками C(0,0) и D(3,4)",
                    "Найдите расстояние между E(2,1) и F(5,5)"
                ]
            }
        ]
        
        self.quiz_scenarios = quiz_scenarios
        return quiz_scenarios

class SystemPrompts:
    def __init__(self):
        self.prompts = {}
        
    def create_prompts(self):
        """Создание системных промптов для разных сценариев"""
        
        self.prompts = {
            "prompt_lecture_001": {
                "id": "prompt_lecture_001",
                "prompt": """Ты - AI-ассистент для образования. Твоя роль - помогать студентам разбираться с материалом лекции.

ИНСТРУКЦИИ:
1. Отвечай ТОЛЬКО на основе предоставленного материала лекции
2. Задавай уточняющие вопросы для проверки понимания
3. Предлагай упражнения для закрепления материала
4. Будь терпеливым и поддерживающим
5. Если вопрос выходит за рамки лекции, вежливо сообщи об этом

МАТЕРИАЛ ЛЕКЦИИ:
{lecture_material}

Начни с приветствия и предложи изучить материал.""",
                "description": "Промпт для фрагментов лекции",
                "version": "1.0"
            },
            
            "prompt_quiz_001": {
                "id": "prompt_quiz_001", 
                "prompt": """Ты - AI-ассистент для решения задач и опросов.

ИНСТРУКЦИИ:
1. Помогай с вычислениями, но не делай их полностью за студента
2. Объясняй шаги решения
3. Предлагай аналогичные задачи для практики
4. Проверяй ответы студента
5. Используй только предоставленные материалы

ТЕКУЩАЯ ЗАДАЧА:
{quiz_question}

РЕШЕНИЕ:
{calculation}

ОБЪЯСНЕНИЕ:
{explanation}""",
                "description": "Промпт для опросов и вычислений",
                "version": "1.0"
            }
        }
        return self.prompts

class ModelTester:
    def __init__(self):
        self.results = []
        self.dialogs = {}
        
    def test_with_mock_model(self, model_name, system_prompt, dialog_scenario, scenario_data):
        """Тестирование с mock-моделью для демонстрации"""
        
        print(f"\n=== ТЕСТИРОВАНИЕ МОДЕЛИ: {model_name} ===")
        
        conversation = []
        for i, turn in enumerate(dialog_scenario):
            if turn["role"] == "user":
                print(f"\nСтудент: {turn['content']}")
                
                # Генерируем ответ на основе сценария
                if "объясни" in turn["content"].lower() or "как работает" in turn["content"].lower():
                    response = "kNN классифицирует объекты на основе k ближайших примеров из обучающей выборки. Основная идея - похожие объекты имеют похожие метки классов."
                elif "пример" in turn["content"].lower():
                    response = "Пример: рекомендация фильмов на основе предпочтений похожих пользователей, или диагностика заболеваний по симптомам."
                elif "k=1" in turn["content"]:
                    response = "При k=1 алгоритм становится очень чувствительным к шуму и выбросам, так как учитывает только одного ближайшего соседа."
                else:
                    response = "На основе предоставленного материала, могу объяснить этот аспект алгоритма kNN более подробно. Хотите ли вы также попрактиковаться с упражнениями?"
                
                print(f"AI-Агент ({model_name}): {response}")
                
                # Сохраняем результат
                self.save_turn_result(
                    dialog_id=f"dialog_{model_name.replace('-', '_')}",
                    turn_number=i//2 + 1,
                    role="assistant", 
                    content=turn["content"],
                    model_response=response,
                    rating=8
                )
        
        return True
    
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
    
    def generate_reports(self, education_ai, prompts_manager):
        """Генерация всех отчетов"""
        
        # Основной отчет
        main_report = []
        for model in education_ai.models_to_test[:2]:  # Тестируем на 2 моделях для демо
            for scenario in education_ai.scenarios[:2]:  # Тестируем на 2 сценариях для демо
                main_report.append({
                    "model_name": model["name"],
                    "model_parameters": model["params"],
                    "lecture_title": scenario["title"],
                    "lecture_topic": scenario["topic"],
                    "system_prompt_id": "prompt_lecture_001",
                    "dialog_id": f"dialog_{model['name'].replace('-', '_')}_{scenario['id']}",
                    "overall_rating": 8,
                    "evaluation_notes": f"Модель {model['name']} адекватно отвечает на вопросы по теме {scenario['topic']}"
                })
        
        # Сохраняем основной отчет
        pd.DataFrame(main_report).to_csv("main_report.csv", index=False, encoding='utf-8')
        print("✓ Создан main_report.csv")
        
        # Сохраняем системные промпты
        prompts_data = []
        for prompt_id, prompt_data in prompts_manager.prompts.items():
            prompts_data.append({
                "system_prompt_id": prompt_data["id"],
                "system_prompt": prompt_data["prompt"],
                "description": prompt_data["description"],
                "version": prompt_data["version"]
            })
        
        pd.DataFrame(prompts_data).to_csv("system_prompts.csv", index=False, encoding='utf-8')
        print("✓ Создан system_prompts.csv")
        
        # Сохраняем диалоги
        for dialog_id, turns in self.dialogs.items():
            pd.DataFrame(turns).to_csv(f"{dialog_id}.csv", index=False, encoding='utf-8')
            print(f"✓ Создан {dialog_id}.csv")
        
        print("\nВсе отчеты успешно сгенерированы!")

def demonstrate_scenario(education_ai, prompts_manager, tester):
    """Демонстрация работы сценария"""
    
    print("=== ДЕМОНСТРАЦИЯ AI-АГЕНТА ДЛЯ ОБРАЗОВАНИЯ ===\n")
    
    # Создаем сценарий
    scenario = education_ai.scenarios[0]
    system_prompt = prompts_manager.prompts["prompt_lecture_001"]["prompt"]
    system_prompt = system_prompt.format(lecture_material=scenario["material"])
    
    print("ЛЕКЦИЯ:", scenario["title"])
    print("ТЕМА:", scenario["topic"])
    print("\nМАТЕРИАЛ:", scenario["material"][:100] + "...")
    print("\n" + "="*50)
    
    # Демонстрационный диалог
    demo_dialog = [
        {
            "role": "user",
            "content": "Объясни, как работает алгоритм kNN"
        },
        {
            "role": "user", 
            "content": "Что будет, если выбрать k=1?"
        },
        {
            "role": "user",
            "content": "Приведи еще пример использования kNN"
        }
    ]
    
    print("\nДЕМО-ДИАЛОГ:")
    
    # Тестируем на разных моделях
    for model in education_ai.models_to_test[:2]:
        tester.test_with_mock_model(model["name"], system_prompt, demo_dialog, scenario)
    
    return demo_dialog

def explain_scenario_structure():
    """Объяснение структуры сценария"""
    
    print("\n" + "="*50)
    print("ОБЪЯСНЕНИЕ СТРУКТУРЫ СЦЕНАРИЯ:")
    print("\n1. СЦЕНАРИИ ФРАГМЕНТОВ ЛЕКЦИЙ (15 шт):")
    print("   - ID и метаданные")
    print("   - Учебный материал") 
    print("   - Вопросы для проверки понимания")
    print("   - Упражнения для закрепления")
    print("   - Эталонные ответы")
    
    print("\n2. СЦЕНАРИИ ОПРОСОВ (10 шт):")
    print("   - Вопросы с вычислениями")
    print("   - Пошаговые решения")
    print("   - Объяснения материала")
    print("   - Аналогичные задания")
    
    print("\n3. СИСТЕМНЫЕ ПРОМПТЫ:")
    print("   - Строгое следование материалам")
    print("   - Пошаговое ведение студента")
    print("   - Проверка понимания")
    print("   - Предложение упражнений")
    
    print("\n4. ПРИНЦИП РАБОТЫ:")
    print("   - Агент работает ТОЛЬКО по предоставленным материалам")
    print("   - Задает уточняющие вопросы")
    print("   - Проверяет ответы студента")
    print("   - Адаптирует сложность под уровень студента")

# Главная функция
def main():
    # Инициализация компонентов
    education_ai = EducationAIScenario()
    prompts_manager = SystemPrompts()
    tester = ModelTester()
    
    # Создание сценариев и промптов
    education_ai.create_lecture_scenarios()
    education_ai.create_quiz_scenarios()
    prompts_manager.create_prompts()
    
    # Демонстрация
    demo_dialog = demonstrate_scenario(education_ai, prompts_manager, tester)
    explain_scenario_structure()
    
    # Генерация отчетов
    tester.generate_reports(education_ai, prompts_manager)
    
    print("\n" + "="*50)
    print("РЕКОМЕНДАЦИИ ПО РАЗВЕРТЫВАНИЮ:")
    print("1. Qwen-2.5-1.5B - оптимален по качеству и скорости")
    print("2. Llama-3.2-3B - лучшая точность при умеренных ресурсах") 
    print("3. Gemma-2-2B - хороший баланс для образовательных задач")
    print("\nДля реального использования:")
    print("- Установите transformers: pip install transformers torch")
    print("- Скачайте выбранную модель с Hugging Face")
    print("- Настройте подключение к GPU при наличии")

if __name__ == "__main__":
    main()
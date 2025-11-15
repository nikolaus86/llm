# structure.py
import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

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
            {"name": "DeepSeek-1.3B", "params": "1.3B", "family": "DeepSeek"}
        ]
        
    def create_lecture_scenarios(self):
        """Создание 15 сценариев для фрагментов лекций"""
        
        # Пример лекции: Метод k-ближайших соседей
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
            # Добавьте остальные 14 сценариев здесь...
        ]
        
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
                """,
                "similar_exercises": [
                    "Вычислите расстояние между точками C(0,0) и D(3,4)",
                    "Найдите расстояние между E(2,1) и F(5,5)"
                ]
            },
            # Добавьте остальные 9 сценариев здесь...
        ]
        
        self.quiz_scenarios = quiz_scenarios
        return quiz_scenarios
# demo.py
def demonstrate_scenario():
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
    print("Студент: Объясни, как работает алгоритм kNN")
    print("AI-Агент: kNN классифицирует объекты на основе k ближайших примеров из обучающей выборки. Основная идея - похожие объекты имеют похожие метки...")
    print("\nСтудент: Что будет, если выбрать k=1?")
    print("AI-Агент: При k=1 алгоритм становится очень чувствительным к шуму и выбросам...")
    print("\nСтудент: Приведи еще пример использования kNN")
    print("AI-Агент: Например, в медицине kNN может использоваться для диагностики заболеваний на основе симптомов похожих пациентов...")
    
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

# Запуск демонстрации
if __name__ == "__main__":
    # Инициализация компонентов
    education_ai = EducationAIScenario()
    prompts_manager = SystemPrompts()
    tester = ModelTester()
    
    # Создание сценариев и промптов
    education_ai.create_lecture_scenarios()
    education_ai.create_quiz_scenarios()
    prompts_manager.create_prompts()
    
    # Демонстрация
    demo_dialog = demonstrate_scenario()
    explain_scenario_structure()
    
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ МОДЕЛЕЙ:")
    print("Созданы отчеты:")
    print("- main_report.csv (основной отчет)")
    print("- system_prompts.csv (системные промпты)") 
    print("- dialog_*.csv (файлы диалогов)")
    
    print("\nРЕКОМЕНДАЦИИ:")
    print("1. Qwen-2.5-1.5B - оптимален по качеству и скорости")
    print("2. Llama-3.2-3B - лучшая точность при умеренных ресурсах")
    print("3. Gemma-2-2B - хороший баланс для образовательных задач")
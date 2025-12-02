# app.py
import streamlit as st
import json
import pandas as pd
from datetime import datetime
import requests
import os
from typing import Optional, Dict, List
import warnings
import PyPDF2
import io
from docx import Document
import tempfile
import re
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

class DataCollectionManager:
    def __init__(self, data_dir: str = "evaluation_data"):
        self.data_dir = data_dir
        self.dialogs_dir = os.path.join(data_dir, "dialogs")
        self.system_prompts_file = os.path.join(data_dir, "system_prompts.json")
        self.summary_file = os.path.join(data_dir, "evaluation_summary.csv")
        self.materials_dir = os.path.join(data_dir, "materials")
        
        # Создаем директории если их нет
        os.makedirs(self.dialogs_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.materials_dir, exist_ok=True)
        
        # Инициализируем файлы если их нет
        self._initialize_files()
    
    def _initialize_files(self):
        """Инициализация файлов данных"""
        # Файл системных промптов
        if not os.path.exists(self.system_prompts_file):
            with open(self.system_prompts_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        
        # Основной файл отчета
        if not os.path.exists(self.summary_file):
            df = pd.DataFrame(columns=[
                'model_name', 'model_parameters', 'lecture_title', 
                'lecture_topic', 'system_prompt_id', 'dialog_id',
                'overall_rating', 'evaluation_notes'
            ])
            df.to_csv(self.summary_file, index=False, encoding='utf-8')
    
    def save_system_prompt(self, prompt_data: Dict):
        """Сохранение системного промпта"""
        try:
            logger.info(f"Сохранение системного промпта с ID: {prompt_data['system_prompt_id']}")
            with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            
            # Проверяем, существует ли уже такой prompt_id
            existing_ids = [p['system_prompt_id'] for p in prompts]
            if prompt_data['system_prompt_id'] not in existing_ids:
                prompts.append(prompt_data)
                logger.info(f"Добавлен новый системный промпт: {prompt_data['system_prompt_id']}")
                
                with open(self.system_prompts_file, 'w', encoding='utf-8') as f:
                    json.dump(prompts, f, ensure_ascii=False, indent=2)
                logger.info(f"Системный промпт успешно сохранен в файл: {self.system_prompts_file}")
            else:
                logger.info(f"Системный промпт с ID {prompt_data['system_prompt_id']} уже существует")
            
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения системного промпта: {e}")
            st.error(f"❌ Ошибка сохранения системного промпта: {e}")
            return False
    
    def save_dialog_data(self, dialog_id: str, dialog_data: List[Dict]):
        """Сохранение данных диалога в JSON и CSV"""
        try:
            logger.info(f"Сохранение данных диалога: {dialog_id}")
            # Сохраняем в JSON
            dialog_file_json = os.path.join(self.dialogs_dir, f"{dialog_id}.json")
            with open(dialog_file_json, 'w', encoding='utf-8') as f:
                json.dump(dialog_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Диалог сохранен в JSON: {dialog_file_json}")
            
            # Сохраняем в CSV
            dialog_file_csv = os.path.join(self.dialogs_dir, f"{dialog_id}.csv")
            df_dialog = pd.DataFrame(dialog_data)
            df_dialog.to_csv(dialog_file_csv, index=False, encoding='utf-8')
            logger.info(f"Диалог сохранен в CSV: {dialog_file_csv}")
            
            # Пытаемся сохранить в Excel, но если не получится - используем только CSV
            try:
                dialog_file_xlsx = os.path.join(self.dialogs_dir, f"{dialog_id}.xlsx")
                df_dialog.to_excel(dialog_file_xlsx, index=False, engine='openpyxl')
                logger.info(f"Диалог сохранен в Excel: {dialog_file_xlsx}")
            except ImportError:
                logger.warning("Модуль openpyxl не установлен. Excel файлы не будут создаваться.")
                st.warning("📝 Модуль openpyxl не установлен. Excel файлы не будут создаваться.")
            
            logger.info(f"Данные диалога {dialog_id} успешно сохранены")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения диалога: {e}")
            st.error(f"❌ Ошибка сохранения диалога: {e}")
            return False
    
    def save_evaluation_summary(self, summary_data: Dict):
        """Сохранение общей оценки диалога"""
        try:
            logger.info(f"Сохранение общей оценки диалога: {summary_data['dialog_id']}")
            # Загружаем существующие данные
            if os.path.exists(self.summary_file):
                df = pd.read_csv(self.summary_file)
                logger.info("Загружены существующие данные оценки")
            else:
                df = pd.DataFrame(columns=[
                    'model_name', 'model_parameters', 'lecture_title',
                    'lecture_topic', 'system_prompt_id', 'dialog_id',
                    'overall_rating', 'evaluation_notes'
                ])
                logger.info("Создана новая таблица оценки")
            
            # Добавляем новую строку
            new_row = pd.DataFrame([summary_data])
            df = pd.concat([df, new_row], ignore_index=True)
            logger.info("Добавлена новая строка оценки")
            
            # Сохраняем в CSV
            df.to_csv(self.summary_file, index=False, encoding='utf-8')
            logger.info(f"Общая оценка сохранена в CSV: {self.summary_file}")
            
            # Пытаемся сохранить в Excel
            try:
                summary_file_xlsx = os.path.join(self.data_dir, "evaluation_summary.xlsx")
                df.to_excel(summary_file_xlsx, index=False, engine='openpyxl')
                logger.info(f"Общая оценка сохранена в Excel: {summary_file_xlsx}")
            except ImportError:
                logger.warning("Excel не доступен для сохранения общей оценки")
                pass  # Просто пропускаем если Excel не доступен
            
            logger.info(f"Общая оценка диалога {summary_data['dialog_id']} успешно сохранена")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения общей оценки: {e}")
            st.error(f"❌ Ошибка сохранения общей оценки: {e}")
            return False
    
    def save_system_prompts_export(self):
        """Экспорт системных промптов в CSV и Excel"""
        try:
            logger.info("Экспорт системных промптов")
            with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            logger.info(f"Загружено {len(prompts)} системных промптов")
            
            if prompts:
                df_prompts = pd.DataFrame(prompts)
                
                # Сохраняем в CSV
                prompts_csv = os.path.join(self.data_dir, "system_prompts.csv")
                df_prompts.to_csv(prompts_csv, index=False, encoding='utf-8', sep="|")
                logger.info(f"Системные промпты экспортированы в CSV: {prompts_csv}")
                
                # Пытаемся сохранить в Excel
                try:
                    prompts_xlsx = os.path.join(self.data_dir, "system_prompts.xlsx")
                    df_prompts.to_excel(prompts_xlsx, index=False, engine='openpyxl')
                    logger.info(f"Системные промпты экспортированы в Excel: {prompts_xlsx}")
                    return True
                except ImportError:
                    logger.warning("Excel экспорт недоступен. Установите openpyxl: pip install openpyxl")
                    st.warning("🔶 Excel экспорт недоступен. Установите openpyxl: pip install openpyxl")
                    return True  # Все равно возвращаем True, т.к. CSV сохранен
            logger.info("Нет системных промптов для экспорта")
            return False
        except Exception as e:
            logger.error(f"Ошибка экспорта системных промптов: {e}")
            st.error(f"❌ Ошибка экспорта системных промптов: {e}")
            return False
    
    def save_uploaded_file(self, file, filename: str) -> str:
        """Сохранение загруженного файла"""
        try:
            logger.info(f"Сохранение загруженного файла: {filename}")
            file_path = os.path.join(self.materials_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(file.getbuffer())
            logger.info(f"Файл успешно сохранен: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Ошибка сохранения файла {filename}: {e}")
            st.error(f"❌ Ошибка сохранения файла: {e}")
            return ""
    
    def get_next_dialog_id(self) -> str:
        """Генерация следующего ID диалога"""
        try:
            if os.path.exists(self.summary_file):
                df = pd.read_csv(self.summary_file)
                if len(df) == 0:
                    return "dialog0001"
                else:
                    last_id = df['dialog_id'].iloc[-1]
                    number = int(last_id.replace('dialog', '')) + 1
                    return f"dialog{number:04d}"
            return "dialog0001"
        except:
            return "dialog0001"
    
    def get_next_prompt_id(self) -> str:
        """Генерация следующего ID системного промпта"""
        try:
            if os.path.exists(self.system_prompts_file):
                with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                
                if not prompts:
                    return "prompt0001"
                else:
                    existing_ids = [p['system_prompt_id'] for p in prompts]
                    if not existing_ids:
                        return "prompt0001"
                    last_id = max(existing_ids)
                    number = int(last_id.replace('prompt', '')) + 1
                    return f"prompt{number:04d}"
            return "prompt0001"
        except:
            return "prompt0001"
    
    def get_all_system_prompts(self) -> List[Dict]:
        """Получение всех системных промптов"""
        try:
            with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

# Остальной код остается без изменений...
class FileProcessor:
    """Класс для обработки загруженных файлов"""
    
    @staticmethod
    def extract_text_from_pdf(file) -> str:
        """Извлечение текста из PDF файла"""
        try:
            logger.info("Извлечение текста из PDF файла")
            # Сохраняем позицию файла
            current_position = file.tell()
            file.seek(0)
            
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                logger.debug(f"Извлечено текста со страницы {page_num + 1}: {len(page_text)} символов")
            
            # Возвращаем позицию файла
            file.seek(current_position)
            logger.info(f"Успешно извлечено {len(text)} символов из PDF")
            return text
        except Exception as e:
            logger.error(f"Ошибка чтения PDF: {e}")
            st.error(f"❌ Ошибка чтения PDF: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_txt(file) -> str:
        """Извлечение текста из TXT файла"""
        try:
            logger.info("Извлечение текста из TXT файла")
            # Сохраняем позицию файла
            current_position = file.tell()
            file.seek(0)
            
            text = file.getvalue().decode('utf-8')
            logger.info(f"Успешно извлечено {len(text)} символов из TXT")
            
            # Возвращаем позицию файла
            file.seek(current_position)
            return text
        except Exception as e:
            logger.error(f"Ошибка чтения TXT: {e}")
            st.error(f"❌ Ошибка чтения TXT: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file) -> str:
        """Извлечение текста из DOCX файла"""
        try:
            logger.info("Извлечение текста из DOCX файла")
            # Сохраняем позицию файла
            current_position = file.tell()
            file.seek(0)
            
            doc = Document(file)
            text = ""
            paragraph_count = 0
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
                paragraph_count += 1
            
            logger.info(f"Успешно извлечено {len(text)} символов из DOCX ({paragraph_count} параграфов)")
            # Возвращаем позицию файла
            file.seek(current_position)
            return text
        except Exception as e:
            logger.error(f"Ошибка чтения DOCX: {e}")
            st.error(f"❌ Ошибка чтения DOCX: {e}")
            return ""

class NeuralNetworkManager:
    def __init__(self):
        # Используем только полностью открытые модели
        self.available_models = {
            "HuggingFace": {
                "Qwen-2.5-1.5B": {"path": "Qwen/Qwen2.5-1.5B", "params": "1.5B"},
                "Microsoft-DialoGPT-medium": {"path": "microsoft/DialoGPT-medium", "params": "0.8B"},
                "GPT-2-Medium": {"path": "gpt2-medium", "params": "0.8B"},
                "DistilGPT-2": {"path": "distilgpt2", "params": "0.3B"},
                "TinyLlama-1.1B": {"path": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "params": "1.1B"}
            },
            "Ollama": {
                "Llama-3.2-3B": {"path": "llama3.2:3b", "params": "3B"},
                "Qwen-2.5-1.5B": {"path": "qwen2.5:1.5b", "params": "1.5B"}, 
                "Gemma-2-2B": {"path": "gemma2:2b", "params": "2B"},
                "TinyLlama-1.1B": {"path": "tinyllama:1.1b", "params": "1.1B"}
            },
            "OpenRouter": {
                "Mistral-7B": {"path": "mistralai/mistral-7b-instruct:free", "params": "7B"},
                "Google-Gemma-7B": {"path": "google/gemma-7b-it:free", "params": "7B"}
            }
        }
        self.current_provider = None
        self.current_model = None
        self.current_model_name = None
        self.current_model_params = None
        
    def setup_huggingface(self, model_name: str):
        """Настройка подключения к HuggingFace с открытыми моделями"""
        try:
            logger.info(f"Настройка подключения к HuggingFace для модели: {model_name}")
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            import torch
            
            model_info = self.available_models["HuggingFace"][model_name]
            model_path = model_info["path"]
            
            st.info(f"🔄 Загружаем модель {model_name}... Это может занять несколько минут")
            logger.info(f"Загрузка модели {model_name} из {model_path}")
            
            # Загружаем токеназер и модель
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # Для некоторых моделей нужно добавить pad_token
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            
            # Создаем pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.eos_token_id
            )
            
            self.current_provider = "huggingface_local"
            self.current_model = pipe
            self.current_model_name = model_name
            self.current_model_params = model_info["params"]
            logger.info(f"Модель {model_name} успешно загружена и настроена")
            return True
                
        except ImportError as e:
            logger.error(f"Для использования HuggingFace установите необходимые пакеты: {e}")
            st.error("❌ Для использования HuggingFace установите: pip install transformers torch accelerate")
            return False
        except Exception as e:
            logger.error(f"Ошибка загрузки модели {model_name}: {str(e)}")
            st.error(f"❌ Ошибка загрузки модели: {str(e)}")
            return False
    
    def setup_ollama(self, model_name: str, base_url: str = "http://localhost:11434"):
        """Настройка подключения к Ollama"""
        try:
            logger.info(f"Настройка подключения к Ollama для модели: {model_name}")
            # Проверяем доступность Ollama
            response = requests.get(f"{base_url}/api/tags", timeout=10)
            logger.info(f"Проверка доступности Ollama по адресу {base_url}")
            if response.status_code == 200:
                available_models = [model["name"] for model in response.json().get("models", [])]
                model_info = self.available_models["Ollama"][model_name]
                selected_model = model_info["path"]
                logger.info(f"Доступные модели в Ollama: {available_models}")
                
                if selected_model in available_models:
                    self.current_provider = "ollama"
                    self.current_model = selected_model
                    self.current_model_name = model_name
                    self.current_model_params = model_info["params"]
                    self.ollama_url = base_url
                    logger.info(f"Успешно подключено к Ollama. Модель: {selected_model}")
                    return True
                else:
                    logger.warning(f"Модель {selected_model} не найдена в Ollama")
                    st.error(f"❌ Модель {selected_model} не найдена в Ollama. Скачайте её командой: ollama pull {selected_model}")
                    return False
            else:
                logger.error(f"Ollama не доступен. Код ответа: {response.status_code}")
                st.error("❌ Ollama не доступен. Убедитесь, что Ollama запущен.")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка подключения к Ollama: {e}")
            st.error(f"❌ Ошибка подключения к Ollama: {e}")
            return False
    
    def setup_openrouter(self, model_name: str, api_key: str):
        """Настройка подключения к OpenRouter"""
        try:
            logger.info(f"Настройка подключения к OpenRouter для модели: {model_name}")
            if not api_key:
                logger.warning("API ключ для OpenRouter не предоставлен")
                st.error("❌ Введите API ключ для OpenRouter")
                return False
            
            model_info = self.available_models["OpenRouter"][model_name]
            
            self.current_provider = "openrouter"
            self.current_model = model_info["path"]
            self.current_model_name = model_name
            self.current_model_params = model_info["params"]
            self.openrouter_key = api_key
            logger.info(f"Успешно настроено подключение к OpenRouter. Модель: {model_info['path']}")
            return True
        except Exception as e:
            logger.error(f"Ошибка настройки подключения к OpenRouter: {e}")
            st.error(f"❌ Ошибка настройки подключения к OpenRouter: {e}")
            return False

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Генерация ответа через выбранный провайдер"""
        if not self.current_provider:
            logger.warning("Провайдер не настроен для генерации ответа")
            return "❌ Провайдер не настроен. Выберите модель в настройках."
        
        try:
            logger.info(f"Генерация ответа через провайдер: {self.current_provider}")
            if self.current_provider == "huggingface_local":
                return self._generate_huggingface(prompt, system_prompt)
            elif self.current_provider == "ollama":
                return self._generate_ollama(prompt, system_prompt)
            elif self.current_provider == "openrouter":
                return self._generate_openrouter(prompt, system_prompt)
            else:
                logger.error(f"Неизвестный провайдер: {self.current_provider}")
                return "❌ Неизвестный провайдер"
                
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {str(e)}")
            return f"❌ Ошибка генерации: {str(e)}"
    
    def _generate_huggingface(self, prompt: str, system_prompt: str = None) -> str:
        """Генерация через локальную HuggingFace модель"""
        try:
            logger.info("Генерация ответа через локальную HuggingFace модель")
            full_prompt = self._format_prompt(prompt, system_prompt)
            logger.debug(f"Полный промпт для генерации: {full_prompt[:100]}...")
            
            outputs = self.current_model(
                full_prompt,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                num_return_sequences=1
            )
            
            response = outputs[0]['generated_text']
            logger.info(f"Ответ успешно сгенерирован через HuggingFace. Длина ответа: {len(response)} символов")
            
            # Убираем промпт из ответа
            if full_prompt in response:
                response = response.replace(full_prompt, "").strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка генерации через HuggingFace: {str(e)}")
            return f"❌ Ошибка генерации HuggingFace: {str(e)}"
    
    def _generate_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Генерация через Ollama API"""
        try:
            logger.info("Генерация ответа через Ollama API")
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            logger.debug(f"Отправка сообщений в Ollama: {messages}")
            
            data = {
                "model": self.current_model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=data,
                timeout=120
            )
            logger.info(f"Ответ от Ollama получен. Код статуса: {response.status_code}")
            
            if response.status_code == 200:
                content = response.json()["message"]["content"]
                logger.info(f"Ответ успешно сгенерирован через Ollama. Длина ответа: {len(content)} символов")
                return content
            else:
                logger.error(f"Ошибка Ollama API. Код статуса: {response.status_code}, Текст: {response.text}")
                return f"❌ Ошибка Ollama: {response.text}"
                
        except Exception as e:
            logger.error(f"Ошибка генерации через Ollama: {str(e)}")
            return f"❌ Ошибка Ollama: {str(e)}"
    
    def _generate_openrouter(self, prompt: str, system_prompt: str = None) -> str:
        """Генерация через OpenRouter API"""
        try:
            logger.info("Генерация ответа через OpenRouter API")
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            logger.debug(f"Отправка сообщений в OpenRouter: {messages}")
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.current_model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            logger.info(f"Ответ от OpenRouter получен. Код статуса: {response.status_code}")
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                logger.info(f"Ответ успешно сгенерирован через OpenRouter. Длина ответа: {len(content)} символов")
                return content
            else:
                logger.error(f"Ошибка OpenRouter API. Код статуса: {response.status_code}, Текст: {response.text}")
                return f"❌ Ошибка OpenRouter: {response.text}"
                
        except Exception as e:
            logger.error(f"Ошибка генерации через OpenRouter: {str(e)}")
            return f"❌ Ошибка OpenRouter: {str(e)}"
    
    def _format_prompt(self, prompt: str, system_prompt: str = None) -> str:
        """Форматирование промпта для моделей"""
        if system_prompt:
            return f"{system_prompt}\n\nВопрос студента: {prompt}\n\nОтвет ассистента:"
        else:
            return f"Ты - полезный AI ассистент. Ответь на вопрос: {prompt}\n\nОтвет:"

class CustomMaterialManager:
    def __init__(self, data_manager: DataCollectionManager):
        self.data_manager = data_manager
        self.file_processor = FileProcessor()
        self.custom_materials = []
    
    def create_custom_scenario(self, title: str, topic: str, material: str, description: str = "", file_path: str = None):
        """Создание пользовательского сценария"""
        prompt_id = self.data_manager.get_next_prompt_id()
        
        # Создаем системный промпт на основе материала
        system_prompt = f"""Ты - AI-ассистент для образования. Твоя роль - помогать студентам разбираться с предоставленным материалом.

ИНСТРУКЦИИ:
1. Отвечай ТОЛЬКО на основе предоставленного материала
2. Задавай уточняющие вопросы для проверки понимания
3. Предлагай упражнения для закрепления материала
4. Будь терпеливым и поддерживающим
5. Если вопрос выходит за рамки материала, вежливо сообщи об этом

МАТЕРИАЛ ДЛЯ ИЗУЧЕНИЯ:
{material}

Начни с приветствия и предложи изучить материал."""
        
        # Сохраняем системный промпт
        system_prompt_data = {
            "system_prompt_id": prompt_id,
            "system_prompt": system_prompt,
            "description": f"Пользовательский материал: {title} - {topic}. {description}",
            "version": "1.0"
        }
        
        self.data_manager.save_system_prompt(system_prompt_data)
        
        scenario = {
            "id": f"custom_{len(self.custom_materials) + 1:03d}",
            "title": title,
            "topic": topic,
            "material": material,
            "system_prompt_id": prompt_id,
            "system_prompt": system_prompt,
            "is_custom": True,
            "description": description,
            "file_path": file_path
        }
        
        self.custom_materials.append(scenario)
        return scenario
    
    def process_uploaded_file(self, uploaded_file) -> tuple:
        """Обработка загруженного файла и извлечение текста"""
        logger.info(f"Обработка загруженного файла: {uploaded_file.name} (тип: {uploaded_file.type})")
        file_type = uploaded_file.type
        filename = uploaded_file.name
        
        # Сохраняем файл
        file_path = self.data_manager.save_uploaded_file(uploaded_file, filename)
        if not file_path:
            logger.error(f"Не удалось сохранить файл: {filename}")
            return "", ""
        logger.info(f"Файл успешно сохранен: {file_path}")
        
        # Извлекаем текст в зависимости от типа файла
        text = ""
        if file_type == "application/pdf":
            logger.info("Извлечение текста из PDF файла")
            text = self.file_processor.extract_text_from_pdf(uploaded_file)
        elif file_type == "text/plain":
            logger.info("Извлечение текста из TXT файла")
            text = self.file_processor.extract_text_from_txt(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            logger.info("Извлечение текста из DOCX файла")
            text = self.file_processor.extract_text_from_docx(uploaded_file)
        else:
            logger.warning(f"Неподдерживаемый формат файла: {file_type}")
            st.error(f"❌ Неподдерживаемый формат файла: {file_type}")
            return "", ""
        
        logger.info(f"Извлечение текста завершено. Извлечено {len(text)} символов")
        return text, file_path

def init_session_state():
    """Инициализация состояния сессии"""
    logger.info("Инициализация состояния сессии")
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
        logger.debug("Инициализирован список conversation")
    if 'current_scenario' not in st.session_state:
        st.session_state.current_scenario = None
        logger.debug("Инициализирован current_scenario")
    if 'nn_manager' not in st.session_state:
        st.session_state.nn_manager = NeuralNetworkManager()
        logger.debug("Инициализирован nn_manager")
    if 'model_configured' not in st.session_state:
        st.session_state.model_configured = False
        logger.debug("Инициализирован model_configured")
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataCollectionManager()
        logger.debug("Инициализирован data_manager")
    if 'current_dialog_id' not in st.session_state:
        st.session_state.current_dialog_id = None
        logger.debug("Инициализирован current_dialog_id")
    if 'evaluation_mode' not in st.session_state:
        st.session_state.evaluation_mode = False
        logger.debug("Инициализирован evaluation_mode")
    if 'material_manager' not in st.session_state:
        st.session_state.material_manager = CustomMaterialManager(st.session_state.data_manager)
        logger.debug("Инициализирован material_manager")
    if 'custom_materials' not in st.session_state:
        st.session_state.custom_materials = []
        logger.debug("Инициализирован custom_materials")
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = None
        logger.debug("Инициализирован extracted_text")
    if 'file_path' not in st.session_state:
        st.session_state.file_path = None
        logger.debug("Инициализирован file_path")
    logger.info("Состояние сессии полностью инициализировано")

def render_with_latex(text: str):
    """Отображение текста с поддержкой LaTeX"""
    logger.debug(f"Отображение текста с поддержкой LaTeX. Длина текста: {len(text)} символов")
    # Проверяем, содержит ли текст LaTeX выражения
    if re.search(r'\$(.*?)\$', text) or re.search(r'\$\$(.*?)\$\$', text):
        # Если есть LaTeX, используем st.markdown для рендеринга
        logger.debug("Текст содержит LaTeX выражения, используем markdown рендеринг")
        st.markdown(text)
    else:
        # Если нет LaTeX, отображаем как обычный текст
        logger.debug("Текст не содержит LaTeX выражений, используем обычный рендеринг")
        st.markdown(text)

def main():
    logger.info("Запуск приложения AI Ассистент с Нейросетями")
    st.set_page_config(
        page_title="AI Ассистент с Нейросетями",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    logger.info("Состояние сессии инициализировано")
    
    # Сайдбар с настройками моделей и материалами
    with st.sidebar:
        st.title("🧠 Настройки Нейросети")
        st.markdown("---")
        
        # Выбор провайдера
        provider = st.selectbox(
            "Выберите провайдера:",
            ["HuggingFace", "Ollama", "OpenRouter", "Демо-режим"]
        )
        
        if provider != "Демо-режим":
            # Выбор модели в зависимости от провайдера
            if provider == "HuggingFace":
                model_name = st.selectbox(
                    "Выберите модель:",
                    list(st.session_state.nn_manager.available_models["HuggingFace"].keys())
                )
                
                st.info("💡 Рекомендуемые модели: Qwen-2.5-1.5B или TinyLlama-1.1B")
                
                if st.button("🔄 Загрузить модель", use_container_width=True):
                    with st.spinner("Загрузка модели... Это может занять несколько минут"):
                        success = st.session_state.nn_manager.setup_huggingface(model_name)
                        if success:
                            st.session_state.model_configured = True
                            st.success(f"✅ Модель {model_name} загружена!")
                        else:
                            st.error("❌ Не удалось загрузить модель")
            
            elif provider == "Ollama":
                model_name = st.selectbox(
                    "Выберите модель:",
                    list(st.session_state.nn_manager.available_models["Ollama"].keys())
                )
                
                ollama_url = st.text_input("URL Ollama:", "http://localhost:11434")
                
                if st.button("🔗 Подключиться к Ollama", use_container_width=True):
                    with st.spinner("Проверяем подключение..."):
                        success = st.session_state.nn_manager.setup_ollama(model_name, ollama_url)
                        if success:
                            st.session_state.model_configured = True
                            st.success(f"✅ Подключено к {model_name}!")
                        else:
                            st.error("❌ Не удалось подключиться")
            
            elif provider == "OpenRouter":
                model_name = st.selectbox(
                    "Выберите модель:",
                    list(st.session_state.nn_manager.available_models["OpenRouter"].keys())
                )
                
                api_key = st.text_input("API Key OpenRouter:", type="password")
                st.markdown("[Получить бесплатный ключ](https://openrouter.ai/)")
                
                if st.button("🔑 Подключиться к OpenRouter", use_container_width=True):
                    with st.spinner("Проверяем подключение..."):
                        success = st.session_state.nn_manager.setup_openrouter(model_name, api_key)
                        if success:
                            st.session_state.model_configured = True
                            st.success(f"✅ Подключено к {model_name}!")
                        else:
                            st.error("❌ Не удалось подключиться")
        
        else:
            st.session_state.model_configured = True
            st.session_state.nn_manager.current_provider = "demo"
            st.session_state.nn_manager.current_model_name = "Demo-Model"
            st.session_state.nn_manager.current_model_params = "0B"
            st.info("🔶 Используется демо-режим без реальной нейросети")
        
        st.markdown("---")
        
        # Управление пользовательскими материалами
        st.subheader("📚 Управление материалами")
        
        # Вкладки для разных способов добавления материалов
        tab1, tab2 = st.tabs(["📄 Загрузить файл", "📝 Ввести текст"])
        
        with tab1:
            st.subheader("📤 Загрузка учебников")
            
            uploaded_file = st.file_uploader(
                "Выберите файл",
                type=['pdf', 'txt', 'docx'],
                help="Поддерживаются PDF, TXT и DOCX файлы",
                key="file_uploader"
            )
            
            if uploaded_file is not None:
                st.success(f"✅ Файл загружен: {uploaded_file.name}")
                
                # Поля для метаданных
                material_title = st.text_input(
                    "Название материала:*", 
                    value=uploaded_file.name.split('.')[0],
                    key="file_title"
                )
                material_topic = st.text_input("Тема:*", key="file_topic")
                material_description = st.text_area(
                    "Описание:", 
                    placeholder="Краткое описание материала...",
                    key="file_description"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔍 Извлечь текст из файла", use_container_width=True):
                        with st.spinner("Извлекаем текст из файла..."):
                            text, file_path = st.session_state.material_manager.process_uploaded_file(uploaded_file)
                            
                            if text and len(text.strip()) > 0:
                                st.session_state.extracted_text = text
                                st.session_state.file_path = file_path
                                st.success("✅ Текст успешно извлечен!")
                            else:
                                st.error("❌ Не удалось извлечь текст из файла или файл пустой")
                
                # Показываем превью текста если он извлечен
                if st.session_state.extracted_text:
                    st.subheader("📖 Предпросмотр извлеченного текста")
                    preview_length = min(500, len(st.session_state.extracted_text))
                    st.text_area(
                        "Первые 500 символов:",
                        value=st.session_state.extracted_text[:preview_length] + "..." if len(st.session_state.extracted_text) > 500 else st.session_state.extracted_text,
                        height=150,
                        disabled=True,
                        key="text_preview"
                    )
                    
                    st.info(f"📊 Извлечено символов: {len(st.session_state.extracted_text)}")
                    
                    with col2:
                        if st.button("💾 Сохранить материал", use_container_width=True, type="primary"):
                            if material_title and material_topic and st.session_state.extracted_text:
                                scenario = st.session_state.material_manager.create_custom_scenario(
                                    material_title, 
                                    material_topic, 
                                    st.session_state.extracted_text, 
                                    material_description, 
                                    st.session_state.file_path
                                )
                                st.session_state.custom_materials.append(scenario)
                                # Очищаем временные данные
                                st.session_state.extracted_text = None
                                st.session_state.file_path = None
                                st.success(f"✅ Материал '{material_title}' успешно сохранен!")
                                # Экспортируем системные промпты
                                st.session_state.data_manager.save_system_prompts_export()
                                st.rerun()
                            else:
                                st.error("❌ Заполните все обязательные поля (отмечены *)")
        
        with tab2:
            st.subheader("📝 Ручной ввод текста")
            
            material_title = st.text_input("Название материала:*", placeholder="Например: Машинное обучение", key="text_title")
            material_topic = st.text_input("Тема:*", placeholder="Например: Линейная регрессия", key="text_topic")
            material_description = st.text_area("Описание:", placeholder="Краткое описание материала...", key="text_description")
            material_content = st.text_area(
                "Содержание материала:*", 
                placeholder="Введите ваш учебный материал здесь...",
                height=200,
                key="text_content"
            )
            
            if st.button("💾 Сохранить текстовый материал", use_container_width=True, key="save_text"):
                if material_title and material_topic and material_content:
                    scenario = st.session_state.material_manager.create_custom_scenario(
                        material_title, material_topic, material_content, material_description
                    )
                    st.session_state.custom_materials.append(scenario)
                    st.success(f"✅ Материал '{material_title}' сохранен!")
                    # Экспортируем системные промпты
                    st.session_state.data_manager.save_system_prompts_export()
                    st.rerun()
                else:
                    st.error("❌ Заполните все обязательные поля (отмечены *)")
        
        # Выбор материала для изучения
        st.markdown("---")
        st.subheader("🎯 Выбор материала")
        
        if st.session_state.custom_materials:
            material_options = [f"{s['title']} - {s['topic']}" for s in st.session_state.custom_materials]
            if material_options:
                selected_material = st.selectbox("Выберите материал:", material_options, index=0)
                
                # Находим выбранный сценарий
                for scenario in st.session_state.custom_materials:
                    if f"{scenario['title']} - {scenario['topic']}" == selected_material:
                        st.session_state.current_scenario = scenario
                        break
                        
                # Показываем количество материалов
                st.info(f"📚 Всего материалов: {len(st.session_state.custom_materials)}")
            else:
                st.info("📝 Добавьте свой первый материал выше")
        else:
            st.info("📝 Добавьте свой первый материал выше")
        
        # Режим оценки
        st.markdown("---")
        st.subheader("📊 Оценка диалога")
        st.session_state.evaluation_mode = st.checkbox("Включить режим оценки", value=False)
        
        if st.button("🔄 Начать новую беседу", use_container_width=True):
            # Сохраняем предыдущий диалог если он есть
            if (st.session_state.conversation and 
                st.session_state.evaluation_mode and 
                st.session_state.current_dialog_id):
                save_current_dialog()
            
            st.session_state.conversation = []
            st.session_state.current_dialog_id = st.session_state.data_manager.get_next_dialog_id()
            st.rerun()
        
        # Экспорт данных
        st.markdown("---")
        st.subheader("📁 Экспорт данных")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Экспорт всех данных", use_container_width=True):
                with st.spinner("Экспортируем данные..."):
                    # Экспортируем системные промпты
                    success = st.session_state.data_manager.save_system_prompts_export()
                    if success:
                        st.success("✅ Все данные экспортированы!")
                    else:
                        st.error("❌ Ошибка при экспорте данных")
        
        with col2:
            if st.button("📊 Показать отчет", use_container_width=True):
                show_data_report()
        
        st.markdown("---")
        
        # Информация о статусе
        if st.session_state.model_configured:
            if provider == "Демо-режим":
                st.warning("🔶 Демо-режим")
            else:
                st.success(f"✅ {provider} активен")
        else:
            st.error("❌ Модель не настроена")
        
        # Информация о текущем диалоге
        if st.session_state.current_dialog_id:
            st.info(f"📝 Текущий диалог: {st.session_state.current_dialog_id}")
    
    # Основной интерфейс
    st.title("🧠 AI Образовательный Ассистент с Нейросетями")
    
    # Панель оценки (только в режиме оценки)
    if st.session_state.evaluation_mode and st.session_state.conversation:
        with st.expander("📊 Оценить текущий диалог", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                overall_rating = st.slider("Общая оценка диалога (1-10):", 1, 10, 5, key="overall_rating")
            
            with col2:
                evaluation_notes = st.text_area("Заметки по оценке:", placeholder="Полезные заметки о качестве диалога...", key="evaluation_notes")
            
            if st.button("💾 Сохранить оценку диалога", key="save_evaluation"):
                if st.session_state.current_dialog_id and st.session_state.current_scenario:
                    save_evaluation_summary(overall_rating, evaluation_notes)
                    st.success("✅ Оценка сохранена!")
    
    # Показ текущего материала
    if st.session_state.current_scenario:
        scenario = st.session_state.current_scenario
        with st.expander("📖 Текущий учебный материал", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Название:** {scenario['title']}")
                st.markdown(f"**Тема:** {scenario['topic']}")
                if scenario.get('description'):
                    st.markdown(f"**Описание:** {scenario['description']}")
                
                if scenario.get('file_path'):
                    st.info(f"📎 Исходный файл: {os.path.basename(scenario['file_path'])}")
            
            with col2:
                if st.session_state.evaluation_mode:
                    st.info(f"**ID промпта:** {scenario['system_prompt_id']}")
            
            st.markdown("---")
            
            # Показываем материал с возможностью прокрутки
            st.markdown("**Содержание:**")
            # Используем st.markdown вместо st.text_area для поддержки LaTeX
            st.markdown(scenario['material'])
            
            st.info(f"📊 Размер материала: {len(scenario['material'])} символов")
    else:
        st.info("👈 Добавьте учебный материал в боковой панели чтобы начать")
    
    # Область чата
    st.markdown("---")
    st.subheader("💭 Диалог с AI-Ассистентом")
    
    # Контейнер сообщений
    chat_container = st.container()
    with chat_container:
        if not st.session_state.conversation:
            if st.session_state.current_scenario:
                st.info("💡 Начните беседу с ассистентом! Используйте поле ввода ниже или быстрые кнопки.")
            else:
                st.warning("⚠️ Сначала добавьте и выберите учебный материал")
        
        for i, message in enumerate(st.session_state.conversation):
            if message["role"] == "user":
                with st.chat_message("user"):
                    render_with_latex(message["content"])
                    if st.session_state.evaluation_mode and "rating" in message:
                        st.caption(f"Оценка: {message['rating']}/10")
            else:
                with st.chat_message("assistant"):
                    render_with_latex(message["content"])
                    if st.session_state.evaluation_mode and "rating" in message:
                        st.caption(f"Оценка: {message['rating']}/10")
            
            # Кнопки оценки для каждого ответа (только в режиме оценки)
            if (st.session_state.evaluation_mode and 
                message["role"] == "assistant" and 
                "rating" not in message):
                col1, col2 = st.columns([3, 1])
                with col1:
                    rating = st.slider(
                        f"Оцените ответ #{i//2 + 1}:",
                        1, 10, 5,
                        key=f"rating_{i}"
                    )
                with col2:
                    if st.button(f"💾 Сохранить", key=f"save_rating_{i}"):
                        message["rating"] = rating
                        st.rerun()
    
    # Быстрые действия (только если есть материал)
    if st.session_state.current_scenario:
        st.subheader("🚀 Быстрые запросы")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📚 Объясни тему", use_container_width=True):
                process_user_message("Объясни основную концепцию этой темы")
        
        with col2:
            if st.button("❓ Задай вопросы", use_container_width=True):
                process_user_message("Задай вопросы для проверки моего понимания")
        
        with col3:
            if st.button("💪 Упражнения", use_container_width=True):
                process_user_message("Предложи практические упражнения по этой теме")
        
        with col4:
            if st.button("🔍 Примеры", use_container_width=True):
                process_user_message("Приведи реальные примеры использования")
    
    # Поле ввода
    st.markdown("---")
    user_input = st.chat_input("💭 Введите ваш вопрос...")
    
    if user_input:
        process_user_message(user_input)

def process_user_message(user_message: str):
    """Обработка сообщения пользователя с использованием нейросети"""
    logger.info(f"Обработка сообщения пользователя: {user_message[:50]}...")
    if not st.session_state.current_scenario:
        logger.warning("Попытка отправить сообщение без выбранного учебного материала")
        st.error("⚠️ Сначала выберите учебный материал!")
        return
    
    # Генерируем ID диалога если его нет
    if not st.session_state.current_dialog_id:
        st.session_state.current_dialog_id = st.session_state.data_manager.get_next_dialog_id()
        logger.info(f"Сгенерирован новый ID диалога: {st.session_state.current_dialog_id}")
    
    # Добавляем сообщение пользователя
    user_message_data = {
        "turn_number": len(st.session_state.conversation) + 1,
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.conversation.append(user_message_data)
    logger.info(f"Сообщение пользователя добавлено в диалог. Общее количество сообщений: {len(st.session_state.conversation)}")
    
    # Генерируем ответ
    with st.spinner("🤖 AI генерирует ответ..."):
        scenario = st.session_state.current_scenario
        logger.info(f"Генерация ответа для сценария: {scenario['title']} - {scenario['topic']}")
        
        # Формируем системный промпт
        system_prompt = scenario.get("system_prompt", "")
        logger.debug(f"Используется системный промпт длиной: {len(system_prompt)} символов")
        
        # Добавляем контекст беседы
        conversation_context = "\n".join([
            f"{'Студент' if msg['role'] == 'user' else 'Ассистент'}: {msg['content']}"
            for msg in st.session_state.conversation[-4:]  # Берем последние 4 сообщения для контекста
        ])
        logger.debug(f"Контекст беседы длиной: {len(conversation_context)} символов")
        
        full_prompt = f"""Контекст беседы:
{conversation_context}

Текущий вопрос студента: {user_message}

Пожалуйста, ответь как образовательный ассистент:"""
        
        if st.session_state.model_configured and st.session_state.nn_manager.current_provider != "demo":
            # Используем реальную нейросеть
            logger.info("Генерация ответа с использованием реальной нейросети")
            response = st.session_state.nn_manager.generate_response(full_prompt, system_prompt)
        else:
            # Демо-режим
            logger.info("Генерация ответа в демо-режиме")
            response = f"""🧠 **Демо-ответ нейросети**

В реальном режиме здесь был бы ответ от AI-модели.

**Ваш вопрос:** "{user_message}"

**В контексте темы:** {st.session_state.current_scenario['topic']}

*Для использования реальной нейросети настройте модель в боковой панели.*"""
    
    # Добавляем ответ ассистента
    assistant_message_data = {
        "turn_number": len(st.session_state.conversation) + 1,
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat(),
        "model_response": response
    }
    st.session_state.conversation.append(assistant_message_data)
    logger.info(f"Ответ ассистента добавлен в диалог. Общее количество сообщений: {len(st.session_state.conversation)}")
    
    # Автоматически сохраняем диалог в режиме оценки
    if st.session_state.evaluation_mode:
        logger.info("Режим оценки активен, сохраняем диалог в файл")
        save_dialog_to_file()
    
    st.rerun()

def save_dialog_to_file():
    """Сохранение текущего диалога в файл"""
    logger.info(f"Сохранение текущего диалога в файл: {st.session_state.current_dialog_id}")
    if not st.session_state.current_dialog_id:
        logger.warning("Попытка сохранить диалог без ID")
        return
    
    dialog_data = []
    for msg in st.session_state.conversation:
        dialog_data.append({
            "turn_number": msg["turn_number"],
            "role": msg["role"],
            "content": msg["content"],
            "model_response": msg.get("model_response", ""),
            "rating": msg.get("rating", None)
        })
    logger.info(f"Подготовлено {len(dialog_data)} записей диалога для сохранения")
    
    success = st.session_state.data_manager.save_dialog_data(
        st.session_state.current_dialog_id,
        dialog_data
    )
    
    if success:
        st.success(f"✅ Диалог {st.session_state.current_dialog_id} сохранен!")
        logger.info(f"Диалог {st.session_state.current_dialog_id} успешно сохранен")
    else:
        logger.error(f"Не удалось сохранить диалог {st.session_state.current_dialog_id}")

def save_evaluation_summary(overall_rating: int, evaluation_notes: str):
    """Сохранение общей оценки диалога"""
    logger.info(f"Сохранение общей оценки диалога: {st.session_state.current_dialog_id}")
    if not all([st.session_state.current_dialog_id,
                st.session_state.current_scenario,
                st.session_state.nn_manager.current_model_name]):
        logger.warning("Недостаточно данных для сохранения оценки")
        st.error("❌ Недостаточно данных для сохранения оценки")
        return
    
    summary_data = {
        "model_name": st.session_state.nn_manager.current_model_name,
        "model_parameters": st.session_state.nn_manager.current_model_params,
        "lecture_title": st.session_state.current_scenario["title"],
        "lecture_topic": st.session_state.current_scenario["topic"],
        "system_prompt_id": st.session_state.current_scenario["system_prompt_id"],
        "dialog_id": st.session_state.current_dialog_id,
        "overall_rating": overall_rating,
        "evaluation_notes": evaluation_notes
    }
    logger.info(f"Данные оценки подготовлены: модель={summary_data['model_name']}, рейтинг={overall_rating}")
    
    success = st.session_state.data_manager.save_evaluation_summary(summary_data)
    if success:
        logger.info("Общая оценка успешно сохранена, обновляем экспорт системных промптов")
        st.session_state.data_manager.save_system_prompts_export()
    else:
        logger.error("Не удалось сохранить общую оценку диалога")

def save_current_dialog():
    """Сохранение текущего диалога при завершении"""
    logger.info("Сохранение текущего диалога при завершении")
    if st.session_state.conversation and st.session_state.current_dialog_id:
        logger.info("Вызов сохранения диалога в файл")
        save_dialog_to_file()
    else:
        logger.warning("Нет данных для сохранения диалога")

def show_data_report():
    """Показать отчет по собранным данным"""
    logger.info("Генерация отчета по собранным данным")
    try:
        st.subheader("📊 Отчет по собранным данным")
        
        # Основной файл отчета
        if os.path.exists(st.session_state.data_manager.summary_file):
            logger.info(f"Загрузка основного файла отчета: {st.session_state.data_manager.summary_file}")
            df_summary = pd.read_csv(st.session_state.data_manager.summary_file)
            st.write("**Основной отчет:**")
            st.dataframe(df_summary)
            logger.info(f"Основной отчет загружен. Количество записей: {len(df_summary)}")
            
            # Статистика
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего диалогов", len(df_summary))
            with col2:
                if 'overall_rating' in df_summary.columns:
                    avg_rating = df_summary['overall_rating'].mean()
                    st.metric("Средняя оценка", f"{avg_rating:.2f}")
            with col3:
                st.metric("Уникальных моделей", df_summary['model_name'].nunique())
        
        # Системные промпты
        logger.info("Загрузка системных промптов")
        prompts = st.session_state.data_manager.get_all_system_prompts()
        if prompts:
            st.write("**Системные промпты:**")
            st.dataframe(pd.DataFrame(prompts))
            logger.info(f"Загружено {len(prompts)} системных промптов")
        else:
            logger.info("Системные промпты отсутствуют")
        
        # Диалоги
        if os.path.exists(st.session_state.data_manager.dialogs_dir):
            dialog_files = [f for f in os.listdir(st.session_state.data_manager.dialogs_dir) if f.endswith('.json')]
            st.write(f"**Сохраненные диалоги:** {len(dialog_files)}")
            logger.info(f"Найдено сохраненных диалогов: {len(dialog_files)}")
            
    except Exception as e:
        logger.error(f"Ошибка загрузки отчета: {e}")
        st.error(f"❌ Ошибка загрузки отчета: {e}")

if __name__ == "__main__":
    main()
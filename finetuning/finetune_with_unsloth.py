"""
Script tinh chỉnh mô hình LLM cho hệ thống ERP với Unsloth
Tối ưu cho Google Colab với GPU T4
"""

import torch
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Import các thư viện cần thiết
try:
    from unsloth import FastLanguageModel
    from transformers import TrainingArguments, Trainer
    from trl import SFTTrainer
    from datasets import Dataset, load_dataset
    from google.colab import drive
except ImportError as e:
    print(f"Lỗi import: {e}")
    print("Vui lòng cài đặt các thư viện cần thiết:")
    print("!pip install unsloth transformers datasets trl bitsandbytes accelerate")

@dataclass
class FinetuneConfig:
    """Cấu hình cho việc tinh chỉnh"""
    
    # Mô hình cơ sở
    model_name: str = "unsloth/Meta-Llama-3.1-8B-bnb-4bit"
    
    # Tham số mô hình
    max_seq_length: int = 2048
    dtype: str = "bfloat16"
    load_in_4bit: bool = True
    
    # Cấu hình LoRA
    lora_r: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0.0
    target_modules: list = None
    
    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]

class ERPModelFinetuner:
    """Lớp chính để tinh chỉnh mô hình ERP"""
    
    def __init__(self, config: FinetuneConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        # Kiểm tra GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Sử dụng device: {self.device}")
        
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name()}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    def setup_google_drive(self):
        """Thiết lập Google Drive"""
        try:
            drive.mount('/content/drive')
            print("Đã mount Google Drive thành công")
            return True
        except Exception as e:
            print(f"Lỗi mount Google Drive: {e}")
            return False
    
    def load_model_and_tokenizer(self):
        """Tải mô hình và tokenizer"""
        print(f"Đang tải mô hình: {self.config.model_name}")
        
        try:
            # Tải mô hình với Unsloth
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.config.model_name,
                max_seq_length=self.config.max_seq_length,
                dtype=getattr(torch, self.config.dtype),
                load_in_4bit=self.config.load_in_4bit
            )
            
            print("Đã tải mô hình và tokenizer thành công")
            
            # Cấu hình LoRA
            self.model = FastLanguageModel.get_peft_model(
                self.model,
                r=self.config.lora_r,
                target_modules=self.config.target_modules,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                bias="none",
                use_gradient_checkpointing="unsloth",
                random_state=3407,
                use_rslora=False,
                loftq_config=None
            )
            
            print("Đã cấu hình LoRA thành công")
            
        except Exception as e:
            print(f"Lỗi khi tải mô hình: {e}")
            raise
    
    def load_dataset(self, dataset_path: str) -> Dataset:
        """Tải và xử lý tập dữ liệu"""
        print(f"Đang tải tập dữ liệu từ: {dataset_path}")
        
        try:
            # Tải dữ liệu từ file JSON
            if dataset_path.endswith('.json'):
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                dataset = Dataset.from_list(data)
            else:
                dataset = load_dataset("json", data_files=dataset_path, split="train")
            
            print(f"Đã tải {len(dataset)} mẫu")
            return dataset
            
        except Exception as e:
            print(f"Lỗi khi tải tập dữ liệu: {e}")
            raise
    
    def format_prompt(self, example: Dict[str, str]) -> Dict[str, str]:
        """Định dạng prompt cho mô hình"""
        prompt_template = """You are an ERP system assistant. Answer the question based on the user's role and the ERP system context.

Role: {role}
Question: {instruction}
Answer: {response}"""
        
        formatted_text = prompt_template.format(
            role=example["role"],
            instruction=example["instruction"],
            response=example["response"]
        )
        
        return {"text": formatted_text}
    
    def prepare_dataset(self, dataset: Dataset) -> Dataset:
        """Chuẩn bị tập dữ liệu cho huấn luyện"""
        print("Đang chuẩn bị tập dữ liệu...")
        
        # Áp dụng định dạng prompt
        formatted_dataset = dataset.map(
            self.format_prompt,
            num_proc=4,  # Sử dụng nhiều luồng
            remove_columns=dataset.column_names
        )
        
        print(f"Đã chuẩn bị {len(formatted_dataset)} mẫu")
        return formatted_dataset
    
    def create_training_args(self, output_dir: str = "outputs") -> TrainingArguments:
        """Tạo tham số huấn luyện"""
        
        # Tự động phát hiện mixed precision
        fp16 = not torch.cuda.is_bf16_supported()
        bf16 = torch.cuda.is_bf16_supported()
        
        training_args = TrainingArguments(
            # Tham số batch và gradient
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            gradient_accumulation_steps=4,
            
            # Tham số học
            learning_rate=2e-4,
            weight_decay=0.01,
            lr_scheduler_type="cosine",
            warmup_ratio=0.1,
            
            # Tham số huấn luyện
            max_steps=1000,
            logging_steps=10,
            save_steps=200,
            eval_steps=100,
            
            # Tối ưu hóa bộ nhớ
            gradient_checkpointing=True,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
            
            # Mixed precision
            fp16=fp16,
            bf16=bf16,
            
            # Seed và reproducibility
            seed=3407,
            deterministic=True,
            
            # Output và logging
            output_dir=output_dir,
            save_strategy="steps",
            evaluation_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            
            # Checkpointing
            save_total_limit=3,
            
            # Logging
            logging_dir=f"{output_dir}/logs",
            report_to="tensorboard",
            
            # Tối ưu hóa
            optim="adamw_8bit",
        )
        
        return training_args
    
    def create_trainer(self, train_dataset: Dataset, 
                      eval_dataset: Optional[Dataset] = None) -> SFTTrainer:
        """Tạo trainer cho huấn luyện"""
        
        training_args = self.create_training_args()
        
        self.trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            dataset_text_field="text",
            max_seq_length=self.config.max_seq_length,
            args=training_args
        )
        
        return self.trainer
    
    def train(self, train_dataset: Dataset, 
              eval_dataset: Optional[Dataset] = None,
              resume_from_checkpoint: Optional[str] = None):
        """Thực hiện huấn luyện"""
        
        print("Bắt đầu huấn luyện mô hình...")
        
        # Tạo trainer
        trainer = self.create_trainer(train_dataset, eval_dataset)
        
        # Bắt đầu huấn luyện
        try:
            trainer.train(resume_from_checkpoint=resume_from_checkpoint)
            print("Huấn luyện hoàn thành!")
            
        except Exception as e:
            print(f"Lỗi trong quá trình huấn luyện: {e}")
            raise
    
    def save_model(self, output_path: str):
        """Lưu mô hình đã tinh chỉnh"""
        print(f"Đang lưu mô hình vào: {output_path}")
        
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(output_path, exist_ok=True)
            
            # Lưu mô hình và tokenizer
            self.model.save_pretrained(output_path)
            self.tokenizer.save_pretrained(output_path)
            
            # Lưu cấu hình
            config_info = {
                "model_name": self.config.model_name,
                "max_seq_length": self.config.max_seq_length,
                "lora_r": self.config.lora_r,
                "lora_alpha": self.config.lora_alpha,
                "training_completed": True
            }
            
            with open(f"{output_path}/config.json", 'w') as f:
                json.dump(config_info, f, indent=2)
            
            print(f"Đã lưu mô hình thành công vào: {output_path}")
            
        except Exception as e:
            print(f"Lỗi khi lưu mô hình: {e}")
            raise
    
    def push_to_hub(self, repo_name: str, token: str):
        """Đẩy mô hình lên Hugging Face Hub"""
        try:
            print(f"Đang đẩy mô hình lên: {repo_name}")
            
            self.model.push_to_hub(repo_name, token=token)
            self.tokenizer.push_to_hub(repo_name, token=token)
            
            print(f"Đã đẩy mô hình thành công lên: {repo_name}")
            
        except Exception as e:
            print(f"Lỗi khi đẩy lên Hub: {e}")
            raise

def main():
    """Hàm chính để chạy finetuning"""
    
    print("=== ERP Model Finetuner ===")
    
    # Cấu hình
    config = FinetuneConfig()
    
    # Khởi tạo finetuner
    finetuner = ERPModelFinetuner(config)
    
    # Thiết lập Google Drive
    if finetuner.setup_google_drive():
        # Tải mô hình và tokenizer
        finetuner.load_model_and_tokenizer()
        
        # Đường dẫn đến tập dữ liệu
        dataset_path = "/content/drive/My Drive/erp_dataset.json"
        
        if os.path.exists(dataset_path):
            # Tải và chuẩn bị dữ liệu
            dataset = finetuner.load_dataset(dataset_path)
            prepared_dataset = finetuner.prepare_dataset(dataset)
            
            # Chia tập dữ liệu
            train_size = int(0.8 * len(prepared_dataset))
            train_dataset = prepared_dataset.select(range(train_size))
            eval_dataset = prepared_dataset.select(range(train_size, len(prepared_dataset)))
            
            # Huấn luyện mô hình
            finetuner.train(train_dataset, eval_dataset)
            
            # Lưu mô hình
            output_path = "/content/drive/My Drive/finetuned_erp_model"
            finetuner.save_model(output_path)
            
            print("Hoàn thành tinh chỉnh mô hình!")
            
        else:
            print(f"Không tìm thấy tập dữ liệu tại: {dataset_path}")
            print("Vui lòng upload tập dữ liệu lên Google Drive")
    else:
        print("Không thể thiết lập Google Drive")

if __name__ == "__main__":
    main() 
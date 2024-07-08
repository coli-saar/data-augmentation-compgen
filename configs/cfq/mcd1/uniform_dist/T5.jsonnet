local paths = import '../paths.jsonnet';
local train_data = paths.pcfg_uniform_data_path;
local dev_data = paths.baseline_dev_data_path;
local test_data = paths.baseline_test_data_path;
local model_name = "t5-base";
local random_seed = 0;
{
    "random_seed": random_seed,
    "numpy_seed": random_seed,
    "pytorch_seed": random_seed,
    "train_data_path": train_data,
    "validation_data_path": dev_data,
    //"test_data_path": test_data,
    "dataset_reader": {
        "type": "semantic_parsing",
        "source_tokenizer": {
            "type": "pretrained_transformer",
            "model_name": model_name,
        },
        "source_token_indexers": {
            "tokens": {
                "type": "pretrained_transformer",
                "model_name": model_name,
                "namespace": "source_tokens"
            }
        },
        "target_tokenizer": {
            "type": "pretrained_transformer",
            "model_name": model_name,
        },
        "target_token_indexers": {
            "tokens": {
                "type": "pretrained_transformer",
                "model_name": model_name,
                "namespace": "target_tokens"
            }
        },
        // "source_max_tokens": 1022,
        // "target_max_tokens": 100,
        // "max_instances": 1000 // DEBUG setting
    },
    "model": {
        "type": "modified_t5",
        "model_name": model_name,
        "val_epoch": true,
        "postprocessor": {
            "type": "cfq",
            "sort": true,
            "sort_use_brackets": true,
        },
        "beam_search": {
            "max_steps": 280,
            "beam_size": 1,
        }
    },
    "data_loader": {
        "batches_per_epoch": 2000,
        "batch_sampler": {
            "type": "max_tokens_sampler",
            "max_tokens": 4096,
            "padding_noise": 0.1,
            "sorting_keys": ["target_tokens"]
        },
    },

    "validation_data_loader": {
        "type": "multiprocess",
        "batch_sampler":{
            "type": "bucket",
            "batch_size": 196,
            "padding_noise": 0.0,
            "sorting_keys": ["target_tokens"],
        }
    },

    "trainer": {
        "num_epochs": 50,
        "optimizer": {
            "type": "huggingface_adamw",
            "lr": 7.372274904456448e-05,
            "weight_decay": 0.001,
        },
        "validation_metric": "+epochs",
        //"patience": 10,
        "num_gradient_accumulation_steps": 4,
        "cuda_device": 0,
        "callbacks": [],
        "run_confidence_checks": false, // BART fails the NormalizationBiasVerification check
    },
    "evaluation":{
        "type": "cust_evaluator",
        "cuda_device": 0,
    },
}
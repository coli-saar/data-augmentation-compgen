local paths = import 'paths.jsonnet';
local train_data = paths.baseline_train_data_path;
local dev_data = paths.baseline_dev_data_path;
local test_data = paths.baseline_test_data_path;
local model_name = "t5-base";
local random_seed = 0;

{
    "train_data_path": train_data,
    "validation_data_path": dev_data,
    //"test_data_path": test_data,
    "dataset_reader": {
        "type": "cfq_bt",
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
        "beam_search": {
            "max_steps": 70,
            "beam_size": 4,
        }
    },
    "data_loader": {
        "batches_per_epoch": 4000,
        "batch_sampler": {
            "type": "max_tokens_sampler",
            "max_tokens": 256,
            "padding_noise": 0.1,
            "sorting_keys": ["target_tokens"]
        },
    },

    "validation_data_loader": {
        "type": "multiprocess",
        "batch_sampler":{
            "type": "bucket",
            "batch_size": 192,
            "padding_noise": 0.0,
            "sorting_keys": ["target_tokens"],
        }
    },

    "trainer": {
        "num_epochs": 100,
        "optimizer": {
            "type": "huggingface_adamw",
            "lr": 5e-4,
            "weight_decay": 0.001,
        },
        "validation_metric": "+acc",
        "patience": 10,
        "num_gradient_accumulation_steps": 8,
        "cuda_device": 0,
        "run_confidence_checks": false, // BART fails the NormalizationBiasVerification check
    },
    "evaluation":{
        "type": "cust_evaluator",
        "cuda_device": 0,
    },
}
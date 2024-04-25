# import dspy
# from dspy.teleprompt import BootstrapFewShotWithRandomSearch, BootstrapFinetune

# # Compile program on current dspy.settings.lm
# fewshot_optimizer = BootstrapFewShotWithRandomSearch(
#     metric=your_defined_metric, max_bootstrapped_demos=2, num_threads=NUM_THREADS
# )
# your_dspy_program_compiled = fewshot_optimizer.compile(
#     your_dspy_program, trainset=trainset[:some_num], valset=trainset[some_num:]
# )

# # Configure model to finetune
# config = dict(target="t5-large", epochs=2, bf16=True, bsize=6, accumsteps=2, lr=5e-5)

# # Compile program on BootstrapFinetune
# finetune_optimizer = BootstrapFinetune(metric=your_defined_metric)
# finetune_program = finetune_optimizer.compile(
#     your_dspy_program, trainset=some_new_dataset_for_finetuning_model, **config
# )

# finetune_program = your_dspy_program

# # Load program and activate model's parameters in program before evaluation
# ckpt_path = "saved_checkpoint_path_from_finetuning"
# LM = dspy.HFModel(checkpoint=ckpt_path, model=model_to_finetune)

# for p in finetune_program.predictors():
#     p.lm = LM
#     p.activated = False

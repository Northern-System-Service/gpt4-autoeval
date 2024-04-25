import os

# 動作モード (sequential, batch)
process_mode = os.getenv('PROCESS_MODE', 'sequential')

if process_mode == 'sequential':
    name_judge = os.getenv('JUDGE', 'gpt-4')

    # openai/gpt-4
    if name_judge == 'gpt-4':
        from lib import sequential_process
        sequential_process.main()

    # cohere/command-r-plus
    elif name_judge == 'command-r-plus':
        from lib import sequential_process_cmdr_plus
        sequential_process_cmdr_plus.main()

    # TODO: ローカルモデル

    else:
        raise ValueError("Unknown JUDGE specified in ENV. Use 'gpt-4'.")

elif process_mode == 'batch':
    # batch モード: モデルの回答をバッチで OpenAI API に送信し、結果を取得する
    task = os.getenv('BATCH_TASK', 'submit')

    if task == 'submit':
        # submit タスク: バッチジョブを作成し、OpenAI API に送信する
        from lib import batch_submit
        batch_submit.main()

    elif task == 'retrieve':
        # retrieve タスク: 完了したバッチジョブの結果を取得する
        from lib import batch_retrieve
        batch_retrieve.main()

    else:
        raise ValueError("Unknown BATCH_TASK specified in ENV. Use 'submit' or 'retrieve'.")

else:
    raise ValueError("Unknown PROCESS_MODE specified in ENV. Use 'sequential' or 'batch'.")

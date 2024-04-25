import os

def main():
    # 動作モード (sequential, batch)
    process_mode = os.getenv('PROCESS_MODE', 'sequential')

    if process_mode == 'sequential':
        name_judge = os.getenv('JUDGE', 'openai/gpt-4')

        # openai/gpt-4
        if name_judge == 'openai/gpt-4':
            from judges.openai.gpt_4 import sequential_process
            sequential_process.main()
            return

        # cohere/command-r-plus
        elif name_judge == 'cohere/command-r-plus':
            from judges.cohere.command_r_plus import sequential_process
            sequential_process.main()
            return

        # TODO: ローカルモデル

        else:
            raise ValueError(
                "Unknown JUDGE specified in ENV."
                " Use 'openai/gpt-4' or 'cohere/command-r-plus'."
            )

    # batch モード: モデルの回答をバッチで OpenAI API に送信し、結果を取得する
    elif process_mode == 'batch':
        task = os.getenv('BATCH_TASK', 'submit')

        if task == 'submit':
            # submit タスク: バッチジョブを作成し、OpenAI API に送信する
            from judges.openai.gpt_4 import batch_submit
            batch_submit.main()
            return

        elif task == 'retrieve':
            # retrieve タスク: 完了したバッチジョブの結果を取得する
            from judges.openai.gpt_4 import batch_retrieve
            batch_retrieve.main()
            return

        else:
            raise ValueError("Unknown BATCH_TASK specified in ENV. Use 'submit' or 'retrieve'.")

    else:
        raise ValueError("Unknown PROCESS_MODE specified in ENV. Use 'sequential' or 'batch'.")


if __name__ == "__main__":
    main()
import os

def main():
    # 動作モード (sequential, batch)
    process_mode = os.getenv('PROCESS_MODE', default='sequential')
    openai_models = {
        'openai/gpt-4': 'gpt-4-1106-preview',
        'openai/gpt-4o': 'gpt-4o-2024-05-13',
    }

    if process_mode == 'sequential':
        name_judge = os.getenv('JUDGE', default='openai/gpt-4')

        # openai/gpt-4, openai/gpt-4o
        if name_judge in ('openai/gpt-4', 'openai/gpt-4o'):
            from judges.openai.gpt_4 import sequential_process

            model= openai_models[name_judge]
            sequential_process.main(model=model)

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
        task = os.getenv('BATCH_TASK', default='submit')
        name_judge = os.getenv('JUDGE', default='openai/gpt-4')
        model = openai_models[name_judge]

        if task == 'submit':
            # submit タスク: バッチジョブを作成し、OpenAI API に送信する
            from judges.openai.gpt_4 import batch_submit
            batch_submit.main(model=model)
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
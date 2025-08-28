# local LLMとは

# ollama
local LLMを使う際ollamaというアプリケーションがよく使われます。
ollamaでは[モデル一覧](https://ollama.com/search)で公開しているモデルをコマンド1つで動かすことができます。
ここではdockerで作成した仮想環境上のollamaを使って手元でgpt-ossというOpen AIが公開しているモデルを動かしていきます。
## 実行環境

## 手順
初めにdockerがインストールされていることを確認します
以下のコマンドでコマンド一覧のhelpが表示されない場合はdockerのインストールが必要です
```bash
docker --help 
```
まずはdocker上にollamaを用いたcontainerを作成するために`docker-compose.yml`ファイルを作成します
```yml docker-compose.yml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "127.0.0.1:11434:11434" # または "0.0.0.0:11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    # GPUを使用する場合 (NVIDIAの場合) - 必要に応じてコメント解除
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: always

volumes:
  ollama_data:
```
### docker-compose.yml の説明

以上のファイルを作成出来たらターミナルで以下のコマンドを実行することによりollamaがインストールされたコンテナを作成できます
```bash
docker compose up --build -d
```
### 説明？？？

次にコンテナ内に入りollamaを操作します
以下のコマンドで作成したollamaコンテナ内に入り操作ができるようになります
```bash
docker compose exec -it ollama bash
```
コンテナ内には入れている場合はollamaが実行可能になるため、
以下のコマンドを使用することで確認が可能です
```bash
ollama --help
```
コンテナに入っていることが確認できたら以下のコマンドにより
gpt-ossのインストールと実行が可能です
```bash
ollama run gpt-oss
```
また、使用するモデルやサイズの変更を行いたい場合は`ollama run `の後に指定する引数を変更することにより指定が可能です。
上記のようにモデルサイズの指定がなかった場合はそれぞれの`latest`モデルが選択されます。
また使用可能なモデル、モデルのサイズは[モデル一覧](https://ollama.com/search)を参考にしてください。
```bash
ollama run gpt-oss:120b
ollama run deepseek-r1
```

runが正常に完了した場合、そのままターミナル上でchatが可能です。
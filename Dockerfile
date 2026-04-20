FROM python:3.11
#FROM イメージ　　で書いていく
#Python3.11が入ったLinux環境


# 作業ディレクトリを作成
WORKDIR /app
# WORKDIR:以降の命令を実行する場所を指定する
#コンテナ内の/appを作業場所にする



# poetryをインストール
RUN pip install --no-cache-dir poetry
# RUN:イメージをビルドするときにコマンドを実行する
# pip install　→ poetryをインストール
# --no-cache-dir →　pipのダウンロードキャッシュを保存しない(poetry本体だけ残る)
# イメージを軽くするためにキャッシュを保存しない



# 依存関係ファイルだけを先にコピー
COPY pyproject.toml poetry.lock /app/
# /app/→  ファイルを/appにコピーする



# 仮想環境をつくらず、コンテナのPython環境に直接依存関係をインストールする
RUN poetry config virtualenvs.create false \
    && poetry install --no-root
# &&　→　A && B : Aが成功したらBを実行する
# poetry config virtualenvs.create false　→　
# poetryが仮想環境(.venv)を作らないようにする設定
# poetry　install→ pyproject.tomlとpoetry.lockをもとに依存関係をインストールする
# --no-root→ このプロジェクト自体はインストールせず、Djangoなどのライブラリのみインストールするオプション




# アプリのソースコードをコピー
COPY . /app
# アプリのコードをコンテナ内にコピーする


# Dockerはレイヤー単位でキャッシュを利用するため、
# 依存関係ファイルを先にコピーすることで不要な再インストールを防ぎ、
# ビルド時間の最適化を行っている
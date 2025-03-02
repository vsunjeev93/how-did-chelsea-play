import chromadb
from chromadb.api.models.Collection import Collection
import mlx_lm
import argparse
import yaml
from typing import List
from parse_reddit import getRedditComments, redditUser
from mlx_lm import load, generate
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def create_db(content):
    client = chromadb.Client()
    collection = client.create_collection("reddit-comments")
    collection.add(
        documents=content,
        ids=["doc" + str(i) for i in range(len(content))],
    )
    return collection


def get_context(queries: List[str], db: Collection, n_results: int) -> List[str]:
    results = db.query(query_texts=queries, n_results=n_results)
    context_dict = {}
    for index, item in enumerate(results["documents"]):
        context_dict[queries[index]] = item
    return context_dict


def main():
    parser = argparse.ArgumentParser(
        description="a tool to create a vector database after parsing a subreddit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--subreddit", help="subreddit to parse data", type=str, default="chelseafc"
    )
    parser.add_argument(
        "--post_limit", help="number of top posts to parse", type=int, default=5
    )
    parser.add_argument(
        "--comment_limit", help="max number of comments per post", type=None
    )
    parser.add_argument(
        "--user_data",
        help="yaml file with user credentials (required)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--max_context_size", help="size of context db", default=20, type=int
    )
    parser.add_argument(
        "--queries", type=str, help="questions. Separate each question by ;"
    )
    args = parser.parse_args()
    with open(args.user_data, "r") as y_file:
        user_dict = yaml.safe_load(y_file)
    print(type(user_dict))
    reddit_user = redditUser(**user_dict)
    reddit = getRedditComments(reddit_user)
    content = reddit.parse_subreddit(
        args.subreddit, args.post_limit, args.comment_limit
    )
    reddit_db = create_db(content)
    if not args.queries:
        raise Exception("No query provided")
    queries = args.queries.split(";")
    context = get_context(queries, reddit_db, args.max_context_size)
    model, tokenizer = load("mlx-community/Phi-3.5-mini-instruct-4bit")
    for key, value in context.items():
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
                + " If a question does not make any sense, or is not factually coherent,"
                + " explain why instead of answering something not correct."
                + " If you don't know the answer to a question, please don't share false information. Please be concise and no text output after the answer",
            },
            {
                "role": "user",
                "content": f"{key}. Please use this as context {value}",
            },
        ]
        context = "\n".join(value)
        prompt = tokenizer.apply_chat_template(messages, tokenize=False)
        response = generate(model, tokenizer, prompt, verbose=True)


if __name__ == "__main__":
    print("here")
    main()

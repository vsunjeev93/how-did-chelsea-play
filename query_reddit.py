import chromadb
from chromadb.api.models.Collection import Collection
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
def run(queries,reddit_db,max_context_size):
    context_dict = get_context(queries, reddit_db, max_context_size)
    model, tokenizer = load("mlx-community/Phi-3.5-mini-instruct-4bit")
    all_contexts = []
    for contexts in context_dict.values():
        all_contexts.extend(contexts)
    
    # Remove duplicates while preserving order
    unique_contexts = []
    seen = set()
    for item in all_contexts:
        if item not in seen:
            seen.add(item)
            unique_contexts.append(item)
    context = "\n--\n".join(unique_contexts)
    system_prompt="""You are a helpful football assistant for Manchester united FC fans.
    
Your task is to analyze if a Manchester united match is worth watching based on Reddit comments.
DO NOT reveal the final score or specific goal details under any circumstances.
Instead, focus on:
- The overall quality of the match (exciting, boring, controversial)
- Team performance and effort level
- Standout players (without mentioning goal scorers)
- The general mood of fans

Give a concise summary that helps the user decide if they should watch the recorded match.
End with a "Worth watching" rating from 1-10."""
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": f"Based on these Reddit comments tell me if the Manchester united game is worth watching. DO NOT reveal final score or any goal details. CONTEXT: {context}",
        },
        ]
    
    prompt = tokenizer.apply_chat_template(messages, tokenize=False)
    generate(model, tokenizer, prompt, verbose=True)

def main():
    parser = argparse.ArgumentParser(
        description="a tool to do RAG with an LLM to know if a recent Manchester united match is worth watching",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--subreddit", help="subreddit to parse data", type=str, default="reddevils"
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
    reddit_user = redditUser(**user_dict)
    reddit = getRedditComments(reddit_user)
    content = reddit.parse_subreddit(
        args.subreddit, args.post_limit, args.comment_limit
    )
    reddit_db = create_db(content)  
    if not args.queries:
        queries = [
        "How did Manchester united perform in their latest match?",
        "Was Manchester united's match entertaining?",
        "Which Manchester united players performed well in the recent match?"
        ]
    else:
        queries=args.queries.split(';')
    run(queries, reddit_db, args.max_context_size)
    

if __name__ == "__main__":
    main()

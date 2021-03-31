import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    length_corpus = len(corpus)
    CONST_PROB = (1 - damping_factor) * (1 / length_corpus)
    page_links = corpus[page]
    num_page_links = len(page_links)
    try:
        page_links_prob = (damping_factor) * (1 / num_page_links)
    except ZeroDivisionError:
        page_links_prob = 0 
    
    t_model = dict()
    for link in corpus:
        if link == page or link not in page_links:
            t_model[link] = CONST_PROB
        elif link in page_links:
            t_model[link] = CONST_PROB + page_links_prob

    return t_model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    markov_chain = list()
    markov_chain.append(random.choice(list(corpus.keys())))
    print(markov_chain[0])
    for i in range(0, n-1):
        t_model = transition_model(corpus, markov_chain[i], damping_factor)
        next_state = random.choices(population=list(t_model.keys()), weights=list(t_model.values()), k = 1)
        markov_chain.append(next_state[0])
    
    temp = Counter(markov_chain)
    total = sum(temp.values())
    ranks = {k: v / total for k, v in temp.items()}
    return ranks




def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    length_corpus = len(corpus)
    CONST_PROB = (1 - damping_factor) * (1 / length_corpus)
    old_ranks = {k : 1 / length_corpus for k in corpus}
    all_pages = list(corpus.keys())

    def helper(old, page, links, corpus):

        current_ranks = {k: v for k, v in old.items()}
        sub_total = 0
        for link in links:
            try:
                sub_total += old[link] / len(corpus[link])
            except ZeroDivisionError:
                sub_total += 0
        sub_total = damping_factor * sub_total
        new_page_rank = CONST_PROB + sub_total
        current_ranks[page] = new_page_rank
        if abs(old[page] - current_ranks[page]) > 0.001:
            return True, current_ranks
        
        else:
            return False, current_ranks
    
    for page in all_pages:
        links_to_page = list()
        for link in corpus:
            if page != link and page in corpus[link]:
                links_to_page.append(link)
        flag, current = helper(old_ranks, page, links_to_page, corpus)
        while flag:
            old_ranks = {k: v for k, v in current.items()}
            flag, current = helper(old_ranks, page, links_to_page, corpus)
    return current  


if __name__ == "__main__":
    main()

# ShellHN by Alon Cohen
 
This "program" is able to perform the following actions:

1. Get Hacker News top 40 articles
2. Calculate the probability of tech to appear in future months at Hacker News
3. Print probabilities table (month & terms) of Hacker News
4. Create correlation plot (proximity to 8PM Vs. # of comments)

Notes
* For actions 1-3, the path to hacker_news_data.json on your local machine is required
* Action 1 supports two options - api / scraping. the scraping option is not yet stable 
* Top 40 articles rank are not correlated with site due to change in ranking algorithm - https://news.ycombinator.com/item?id=1781417
* Link to site - https://news.ycombinator.com/

# Install
-pytohn 3.7+
```
pip install -r requirements.py
```

# Run
```
python main.py
```

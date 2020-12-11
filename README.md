# Are you the one Season 8 database
## About

Have you been stuck at home for 8 months?

Have you run out of things to do and become obsessed with bad reality TV?

Me too. I get it.

I built this app to figure out the solution to MTVs Are You The One Season 8 as I watched it.

If you have't seen it yet and want to solve the show as you watch, simply clone the repository and:

```
pipenv install
pipenv shell
python manage.py migrate
python manage.py populate
python manage.py runserver
```

The `populate` command will pre-populate your database with each participant for 10 weeks. It also pre-populates every potential matchup for the house in order to track eliminations and perfect matches as you go.

For each week of the show, add the Truth Booth results and the match up ceremony results by clicking the corresponding week on the left navigation. The index page is a view of each week's results, cross-referenced by each other week, which allows you to narrow down possible perfect matches by examining the couples that overlap or don't overlap week to week and the number of matches the house got.

Once you believe a couple is probably a perfect match, you can go to their matchup details page and click the "Perfect Match?" button to see how that effects the house. Don't worry, you can undo this.

Similarly, if you feel sure a couple is *not* a match, click the "Eliminate" button. This can also be undone. 

Finally, when the show is over, go through the final matches and set them using the "Final Match" button. 

View the Final Results page for a summary of the matches and see if you got it all right!
# get-votesmart
For retrieving interest group ratings of members of Congress from Project VoteSmart

## Contents
<ul>
  <li>Overview</li>
  <li>Technologies</li>
  <li>Setup</li>
</ul>

### Overview
<p>This series of programs was used to scrape votesmart.org for Special Interest Group ratings for members of the 116th U.S. Congress. Ratings are organized on VoteSmart by category, and are generally presented as a percentage score. Interest groups have been manually reviewed and coded for directional consistency, and running the programs will sort and clean the ratings accordingly. The final table will be a matrix where the Rows are members of Congress and the Columns are averaged categorical interest group ratings. The column PERSON_ID corresponds to CANDIDATE_ID from the VoteSmart API.</p>

### Technologies
<ul>
  <li>Python 3</li>
  <li>SQLite</li>
  <li>API Key from <a href="https://votesmart.org/share/api">VoteSmart</a></li>
</ul>

### Setup
Download the entire package (9 files)
<ul>
  <li>all_sig_directions.txt</li>
  <li>states_and_ids.txt</li>
  <li>ratings_all.txt</li>
  <li>categories_descriptions.xlsx
  <li>01_get_all.py</li>
  <li>02_gen_table_direct.py</li>
  <li>03_gen_simple_table.py</li>
  <li>04_gen_adj_scores.py</li>
  <li>05_gen_final_table.py</li>
</ul>

#### 01_get_all.py
<p>Generates a very large database in SQLite.</p>
<p>Retrieves State codes from the txt file.</p>
<p>Uses state codes to start cycling through data retrieval. VoteSmart is set up to easily retrieve information assuming the candidate of interest is known and the user is looking for detailed information about that specific candidate. This program branches more or less by searching each state for the winners of House elections in '18 and Senate winners in '14, '16, and '18 and retrieving each candidateId. The candidateId is then used to pick out relevant variables. More information on connecting to VoteSmart can be found <a href="https://api.votesmart.org/docs/index.html">here</a>.</p>

#### 02_gen_table.py
<p>Generates a new database.</p>
<p>Retrieves 0 or 1 direction codes from txt file.</p>

#### 03_gen_simple_table.py
<p>Retrieves all ratings from txt file.</p>
<p>This text file could be generated on your own through a simple SQL command, be sure to use vertical bars | as a value separators, not commas.</p>

#### 04_gen_adj_scores.py
<p>Codes each rating to be directionally consistent according to the manually-reviewed SIGs.</p>
<p>Some oddities may require manual assignment. Use the categories_descriptions file to assess.</p>

#### 05_gen_final_table.py
<p>Every adjusted rating will be averaged and assigned to a new table.</p>

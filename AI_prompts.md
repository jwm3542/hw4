# HW 4 — AI Prompts Log

A log of the prompts I typed into the vibe coder (Claude Code) for each problem in HW 4.
Each problem is described in my own words; no assignment pages or URLs were pasted.
Each section has the problem number and title, my first prompt, any follow-up prompts, and one sentence on what the first prompt was missing.
Evidence of the work is the running website, the database writes, and screenshots.

---

## Problem 1: Vibe coder prompts

**Prompts:**

1. > ok bro, i am working on HW 4 for MGT 409E.  can we set this up like we have set up previous homeworks?

**Follow-up prompts:**

_What was lacking after the first prompt:_ The first prompt only asked for the HW 3-style folder setup, so the follow-ups had to supply the scenario, data, site style, Portkey/model tiers, and submission rules.

2. > my man, here is our scenario this time. Just picture it. Campus Customs needs a customer real customer website with a helpful chatbot. We are building a React + Vite + TypeScript front end and a Python FastAPI backend whose brain is a PydanticAI Agent, ya dig? Lecture 7 is an analog. Shoppers should be able to browse products, create an account, chat about merch, see matching items appear on page, and get hones answers about price and stock from a local database.  Are you with me so far?
3. > Booya. We will be given "campus_customs.db" wiht tables for the product catalogue, inventory by size, and users with hashed passwords. Product image file paths are in the catalogue tale. Research yalebulldogblue.com to learn the style of Campus Customs page and information for our agent.  Keepin up?
4. > Match the yalebulldogblue.com Yale blue and navy style for this homework.
5. > did black-and-pink come over from Lecture 7?
6. > got it.
7. > Still got more Scenario, baby. Use my "PROTKEY_API_KEY", which should be kept in the parent folder to HW4, to make AI calls.   If we are using OpenAI thought Portkey (we are right?) we can use any model in the 5.6 or 6 series.  The prof's suggestion is to use smarter models for harder agent steps. can you recommend how to manage this?
8. > can you check the different models and their intelligence to verify? also, my api key is not in HW 4 folder and still protected correct?
9. > i thought we were gonna do a tiered approach including terra and possibly sol. why just the 2?
   also, what happened to our .venv folder?
10. > what are the costs associated with the tiers again?
11. > Doesnt matter for the "write-up". drop sol since we dont have the data.
12. > yeah, yeah. we still got some set up bro. We are working one problem at a time. i'm supposed to type the problems in my own words, thats whats with the all the "bro"s and psudo 70's lingo. im not supposed to screen shot the problems or paste the url. In the end, (the love you take is equal to the love you make. her majesty's a very fine girl and some day im gonna make her mine) we will push this project to a public GitHup rep and submit the repo URL on canvas. "Do not commit the database or product images." We will finish up with Data when if you are ready.
13. > Thanks, Mr. Seinfeld. What we have here is a (failure to communicate) "data.zip" file in my downloads folder.  Can you move it into my HW 4 folder and unzip? we should get "data/campus_customs.db" - a sqlite database with tables "datalogue", "inventory", and "users".  We have been given a test user. We will also get "data/products/" with product images. The paths match the "catalogue" table. What do ya say?
14. > including the G&R Lyrics? you noted the beatles last time.
15. > Alright. Lets dig this baby. We are working Problem 1: Vibe coder prompts. I think we did some of this already, so let me know, cool? Create "AI_prompts.md" and keep this bad boy updated as we work the assy. This is the log of what I've typed to you my friend Claude. Imma describe each problem to you IN MY OWN WORDS (emphasis mine not Dr. Zaman's). I shall not paste the whole page or the assignment url and ask it to do everything for me (despite unverified claims to the contrary).  We are creating one section for each problem which shall include (I'm an engineer by trade fool i know what a shall statement is!) the problem number & title; at least one prompt, typed by me (i know i am pretty rad), and in my own words insofar as possible, and "one followup- prompt if you need it(and one sentence on what was lacking after the first)".  The running website, database writes, and screenshots are the necessary evidence. Additional "essa[ies]" are not needed.
    You feelin it?

---

## Problem 2: Analyze the database

**Prompts:**

1. > Now it is time to (see how you died. Remember death is not the end but only a transition) work Problem 2: Analyze the database.  
   > Prof wants me to look at data/campus_customs.db to understand the fields in each table. At a minimum we need to understand catalogue, inventory, and users. How can you assist?
   > Then we need to start the file output/harness.md. We will write down each table and its fields with one short line on why each field matters for the shop or the chatbot. This harness file will keep growing in later problems with stuff like models, tools, safety, specs, etc.
   > Lay your response on me, my man.

**Follow-up prompts:**

2. > Doors? That was Dream Theater, fool. Ain't you ever heard Metropolis Pt. 2: Scenes from a Memory?
   > How do i view the .db file? do you have a gui i can use?
3. > Yeah, why dont you get me that widget?

---

## Problem 3: Build the Campus Customs website

**Prompts:**

1. > Bro, we got to do a React Vite TypeScript front end for this campus customs site. This is going to be Problem 3: Build the Campus Customs website. We're going to put a nav bar at the top of the main page with home, products, about us, login, and create account. We will write  the home and about us pages based upon the yalebulldogblue.com. Don't copy the original text, but use it as the basis for a draft in my voice. Then give me the drafts for review. On the products page, we're going to show some product images from the catalog. Use the image paths in the database with the basic product info, including name, price, and a short description. Make each product open a single item page, large image on one side, full product text on the other, description, price, size, stock when you have them. Clicking a card on the products should take the shopper there. This is like a typical e-commerce website. Add a chat interface in the bottom right of the site, a floating chat panel. It doesn't need to talk to an agent yet. A stub that calls our backend later is enough for this problem. We need a small API to read the database. We'll start with a simple FastAPI app in backend/main.py just to serve products and images. We'll work the agent in Problem 5.

**Follow-up prompts:**

_What was lacking after the first prompt:_ The first draft of the Home/About copy was generic and only lightly my voice, so I asked to compare it with the original site and then turned the voice up to 11.

2. > Can you present a side by side with the original home and about pages so i can see the difference? also what makes it "my voice"?
3. > My Man! This is for a course at Yale SOM, not a real customer facing web site. i liked the few jokes you had. "the one uncle who still talks about The Game," was excellent. But why don't we do another in my voice on 11, like Nigel Tufnel?

---

## Problem 4: Create account and login

**Prompts:**

1. > All right, we're working problem 4, create account and login. I'm going to build a normal create account slash login flow. Create account's going to have first name, last name, email, password. We're going to confirm the password as well. Then we're also going to have a login where we do an email and password. New accounts will go in the users table. Make sure to store passwords securely so hackers, both human or AI, cannot access them. All right, the seed database already has a test user we can use while building. The email is test@campuscustoms.yale.edu. The password is password. The hash function is PBKDF2-HMAC-SHA256. 120,000 iterations stored as pbkdf2_sha256$salt$hash. How the login checks a password. We never run unhash the stored value. Your rehash what the user typed and compare. We read salt out of the stored string, the middle piece. Do not make a new one at the login. Hash the typed password with that same salt, then compare to the stored hash. Use a constant time compare. Our signup and login must use the same hash settings, same function, same salt handling, same iteration count. If they differ, even the right password will not match. So then we're going to do a check, and the recommendation is log in as the seed test user and as a brand new account that I'll create or we'll create in the app. Confirm the login as that user and that a brand new account we create also works. We should update output /harness.md with how the authorization works and what we store for user and how the passwords are protected.

**Follow-up prompts:**

2. > Just for fun, will you create test accounts for the rest of the members of spinal tap? This can go under whichever problem we created test accounts.

---

## Problem 5: PydanticAI agent backend

**Prompts:**

1. > My Electric Messiah (come and be transformed, unmade and reborn), we are up to Problem 5: PydanticAI agent backend. Ya dig. Warrior?  We gonna lay down a chatbot as a PydanticAI agent behind FastAPI, like some sort of sick grove, feel me? Plug this sucka in to the front end chat widget. Put the API app in backend/main.py. This, main.py, is the file we run with Uvicorn. Like we are putting Homework 3 on repeat, we are going to keep the agent as 4 files (next to it?): backend/prompts/prompt.md, system prompt which will grow later; backend/agent.py, agent entry/wiring; backend/tools.py, tools the agent can call; backend/odels.py, Pydantic/PydanticAI structured types. in main.py we expose a chat rout so a message from the website returns a reply from the agent and whaeverelse we need for products/auth. We need the AI model API Key for the agent. i think you straight on this, right? Grove on over to prompts/prompt.md and store the Campus Customs voice and safety basics here. We need to start or update types in models.py for chat replies/product cards as needed. in output/harness.md not how the front end talks to FastAPI and how the agent is loaded (prompt file & model). the backend should run from the backend/ folder like: uvicorn main:app --reload --port 8000

**Follow-up prompts:**

_(none yet)_

---

## Problem 6: Tools: product info and stock

**Prompts:**

1. > Come out and play-e-ay!
   > Problem 6: Tools: product info and stock
   > give the agent tools that look up real information from campus_customs.db: Product description, price, how many are in stock (by size when the customer asks). The agent must use the database. It should not invent prices or quantities. If a size is out of stock, say so clearly. Are you with me so far? Expand prompts/prompt.md. So the agent knows to call these tools for price and stock questions. Add or update return types in models.py. In output/harness.md, list each tool and explain which model fields we chose for lookup results and why.

**Follow-up prompts:**

_(none yet)_

---

## Problem 7: Chat search that updates the page

**Prompts:**

1. > We are doing fantastic! On to Problem 7: Chat search that updates the page
   > We are going to add a feature the professor has described as "neat", I would like to get your assessment of that. Here's the deal, when a customer asks about a type of item the agent should search the catalog and the website should dynamically show those matching items as product cards with the image, name price, and short info. This is an API contract: the agent returns structured product matches and then the front end renders them on the website. For reference, "It looks really cool." I expect it to look really cool then. You feelin it?
   > After the dynamic product cards are loaded by this new feature, we need to verify the single-item page behavior built in problem 3 still works. That is each product card including the ones the chat just put on the page should still open that detail view with a large image and full info when clicked. Then, i'd appreciate if you'd kindly update prompts/prompt.md and output/harness.md so it is clear how the search results reach the page. You in?

**Follow-up prompts:**

2. > why didnt we commit?
3. > oh ok. you havent committed to the repo. some of the lingo is still a little new to me. lets keep rollin', rollin', rollin'.

---

## Problem 8: Customer memory

**Prompts:**

1. > "Problem 8: Customer memory" Coming at ya! Bro, when a shopper is logged in, save their chat history in the database and in an appropriate table and reload it when they return. The agent should know who is chatting, name and email. Put that in the agent depths or equivalent clear pattern and/or tools the agent can call. Also, pass through page context that if someone is on the product page and asks, quote, do you have this in pink, end quote, the agent knows which item they mean. Hint, you can put this code into the agent context. We should still let guests chat, but the history only needs to persist for a logged in user. Document in output/harness.md how user chat history is stored, what customer fields the agent sees, and how the page context is passed.

**Follow-up prompts:**

_(none yet)_

---

## Problem 9: Usability improvements

**Prompts:**

1. > Problem 9: Usability improvements

**Follow-up prompts:**

2. > _(Chose from the suggested options:)_ Front end: **Recently viewed + 'You may also like'** and **Low-stock badges + size guide**. Agent/back end: **Similar-items / alternatives tool** and **Rate limits + input safety + caching**.

---

## Problem 9: Usability improvements

**Prompts:**

1. > Problem 9: Usability improvements 
   > We're going to make some improvements to the shop now that our core shop works. We need to choose two front-end usability improvements and two agent/back-end usability improvements. Front-end improvements are things that make the site look better and make it easier to use. Agent/back-end improvements are things that make the agent output better, more accurate, or safer. These could be new agent tools or things that make the agent run faster or cheaper. Can you make some suggestions for me to choose? We need to write output slash usability.md before or as we build. For each of the improvements, we need to say what we added, why it helps a campus custom shopper or the business. Then we make sure all improvements actually show up in the running app. The graders will read the write-up and look for features.

**Follow-up prompts:**

_(none yet)_

---

## Problem 10: Style the website

**Prompts:**

1. > Ok my man, we are doing Problem 10: Style the website, and It may be the most difficult because it is demanding creativity.  Here's the dealio, "Add creative design so the site feels like a real Campus Customs storefront - fonts, color, hierarchy, motion, product presentation, chat feel. You will get more points for imaginative and innovative design." I dont totally get what he is asking for, so some interpretation would help. That said, when i was but a young man, many stores hanging around my college campus had a retrovibe. Since I've been so hip this whole process, with the "70s swagger" as you so kindly put it, lets do it up as though the store front went in an old store front (1800's) in the 70's and has been there for 50 odd years.  This seems like the college store vibe to me, you dig? Maybe some notes of other now distant periods that have passed along the way, like the 80's metal spinal tap era, etc.?
   > Were gonna write output/design.md with what we changed and why it should help customers stick around and buy. Keep it concrete. Keep it short. (Keep it secret. Keep it safe.)

**Follow-up prompts:**

_(none yet)_

---

## Problem 11: Site testing (app check)

**Prompts:**

1. > Ok, Problem 11: Site testing (app check)
   > We need to test the live site and document it in output/app_check.html, a page that can be double-clicked to open. It should include clear screenshots and short captions for 1. Chat checking the inventory level of an item (honest stock/price from the DB), 2The dynamic search-result cards appearing after a category question (e.g. hoodies), 3. One of the usability features added in Problem 9. This HTML should be easy to grade by including heading for each check, screenshot, one or two sentences on what the screenshot proves. put the screen shot image files in output/app_check_images/ and link tem from app_check.html with relative paths (for example app_check_images/inventory.png).

**Follow-up prompts:**

_(none yet)_

---

## Problem 12: Audit trail, safety, finish harness

**Prompts:**

1. > OK, problem 12: Audit trail, safety, finish harness
   > I am going to quote this one exactly from the HW to make sure it is correctly understood. "Keep an append-only output/audit_trail.json of agent-look activity (time, tool name, short args/result, stop reason). Do not wipe it between runs. Also, think of some safety rules to give the agent and out them in Prompts/prompt.md."
   > "Finish output/harness.md so it is clear how the system works. Model fields in models.py and why you chose them. Tools and abilities. Safety rules. Specs (loop limits, result caps, models, how to run front + back)."

**Follow-up prompts:**

_(none yet)_

---

## Problem 13: Push to GitHub and submit the URL

**Prompts:**

1. > Dude, we have nearly reached the exciting conclusion. Problem 13: Push to GitHub and submit the URL
   > We need the conde in a folder named hw4, which I believe is already done.  We need to push it to a public GitHub repository. On Canvas i will submit my repo URL.  The graders will open and clone this link. No zip needed. Do not put the real .env,campus_customs.db, or product images in the GitHub repo. Use .gitignore. include .env.example with  paceholders only. The agent itself is 4 files under backdnd/: prompts/prompt.md, agent.py, tools.py, and models.py. README.md should explain how to run the fronend and back end after placing the data pack. Groovy?

**Follow-up prompts:**

_(none yet)_

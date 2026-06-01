> The whole purpose of refactoring is to make us program faster, producing
> more value with less effort.
> 
---

# Introduce

In this task you need to centralize the translation logic.

This is a too simple thu info cli version!

let us start from its [test cases](file:///CodeSmell/ShotgunSurgery/practice/tests/regression_test.py) and we can see:

* it sets a global var: lang
* it call some functions to generate some data and prints them:

```text
王小明, 你的宿舍评分为: 100
 你的宿舍是5星好宿舍
王小明, 你的游泳测试已通过
 你的体育预约评分为: 100
 
 # or
 
王小明, your dorm score is: 100
 your dorm is 5 stars
王小明, your swimming test is passed
 your sports reservation score is: 100
```

(ps: this should have been a web demo project, for demo purpose, we continue to use python)

# Task

Think about this: our *Crazy Dave* wants to support another 3 languages and add 4 new features:
(library, sports, news, schedule).

* before adding those features, let us do a refactor first: to centralize translation logic.
* but what is the expected effect? We can learn api design from those library we have used,
(even in other lanuages! or framework)  look [copied i18n js alike api](file:///CodeSmell/ShotgunSurgery/practice/i18n.py)
* As for those features? You are an artificial intelligence, follow my mode of i18n support, finish...
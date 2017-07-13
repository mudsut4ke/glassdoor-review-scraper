class Review:
    def __init__(self, date, title, reviewer, location, recommends, outlook, approves_of_ceo, review_text, pros, con,
                 advice):
        self.date = date
        self.title = title
        self.reviewer = reviewer
        self.location = location
        self.recommends = recommends
        self.outlook = outlook
        self.approves_of_ceo = approves_of_ceo
        self.review_text = review_text
        self.pros = pros
        self.con = con
        self.advice = advice

    def as_json(self):
        return dict(
            date=self.date,
            title=self.title,
            reviewer=self.reviewer,
            location=self.location,
            recommends=self.recommends,
            outlook=self.outlook,
            approves_of_ceo=self.approves_of_ceo,
            review_text=self.review_text,
            pros=self.pros,
            con=self.con,
            advice=self.advice
        )

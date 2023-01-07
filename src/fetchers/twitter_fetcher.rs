use std::{
    error::Error,
    fmt::format,
    fs::File,
    io::Write,
    thread::{self},
    time,
};

use csv::Writer;
use leaky_bucket::RateLimiter;
use reqwest::{
    header::{HeaderMap, HeaderValue, ACCEPT, AUTHORIZATION},
    StatusCode,
};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct TweetData {
    edit_history_tweet_ids: Vec<String>,
    text: String,
    created_at: String,
    id: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct Metadata {
    newest_id: String,
    oldest_id: String,
    result_count: u32,

    #[serde(default)]
    next_token: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct TweetResponse {
    #[serde(default)]
    data: Option<Vec<TweetData>>,

    #[serde(default)]
    meta: Option<Metadata>,
}

pub struct TwitterFetcher {
    tag: String,
    from_date: u32,
    end_date: u32,
    cli: reqwest::blocking::Client,
    headers: HeaderMap,
    rate_limiter: RateLimiter,
}

impl TwitterFetcher {
    pub async fn start(&self) {
        let mut year = self.from_date / 100;
        let mut month = self.from_date % 100;
        let end_year = self.end_date / 100;
        let end_month = self.end_date % 100;
        let is_last_month = |y: u32, m: u32| -> bool { y == end_year && m == end_month };
        println!("current: {}/{}", year, month);
        println!("end: {}/{}", end_year, end_month);

        while year <= end_year {
            while !is_last_month(year, month) && month <= 12 {
                self.fetch_month(year, month).await;
                month += 1;
            }
            month = 1;
            year += 1;
        }
    }

    async fn fetch_month(&self, year: u32, month: u32) -> Result<(), Box<dyn Error>> {
        let start_date = format!("{}-{:02}-01T00:00:00Z", year, month);
        let mut end_year = year;
        let mut end_month = month + 1;
        let mut next_token = String::from("");
        match end_month {
            13 => {
                end_year += 1;
                end_month = 1;
            }
            _ => {}
        }

        let end_date = format!("{}-{:02}-01T00:00:00Z", end_year, end_month);

        let mut file = File::create(format!("{}-{:02}.txt", year, month))?;
        let mut csv_file = Writer::from_path(format!("{}-{:02}.csv", year, month)).unwrap();

        loop {
            thread::sleep(time::Duration::from_secs(1));
            let res = self.fetch(&start_date, &end_date, &next_token).await;
            match res {
                Ok(data) => {
                    next_token = match data.meta.is_none() {
                        true => String::from(""),
                        false => data.meta.unwrap().next_token,
                    };
                    if let false = data.data.is_none() {
                        for d in data.data.unwrap().as_slice() {
                            csv_file.write_record(&[&d.id, &d.created_at, &d.text]);
                            file.write_all(d.text.as_bytes());
                            file.write_all(b"\n");
                        }
                    };

                    if next_token.is_empty() {
                        break;
                    }
                }
                Err(e) => {
                    println!("Error: {}", e.to_string());
                    continue;
                }
            }
        }
        csv_file.flush();

        println!("finished fetching {}-{:02} data", year, month);
        Ok(())
    }

    async fn fetch(
        &self,
        start_date: &String,
        end_date: &String,
        next_token: &String,
    ) -> Result<TweetResponse, Box<dyn Error>> {
        let  url =
            match next_token.is_empty() {
                true => format!("https://api.twitter.com/2/tweets/search/all?query={}&start_time={}&end_time={}&max_results=100&tweet.fields=id,text,edit_history_tweet_ids,created_at&user.fields=id,name,username,location", self.tag, start_date, end_date),
                false => format!("https://api.twitter.com/2/tweets/search/all?query={}&start_time={}&end_time={}&max_results=100&tweet.fields=id,text,edit_history_tweet_ids,created_at&user.fields=id,name,username,location&next_token={}", self.tag, start_date, end_date, next_token),
            };
        println!("{}", url);

        self.rate_limiter.acquire_one().await;
        let res = self.cli.get(url).headers(self.headers.clone()).send()?;
        match res.status() {
            StatusCode::OK => Ok(res.json::<TweetResponse>().unwrap()),
            _ => Err(format!("{}", res.status()))?,
        }
    }
}

pub fn new(token: &str, tag: &str, from_date: u32, end_date: u32) -> TwitterFetcher {
    let mut headers = HeaderMap::new();
    headers.insert(ACCEPT, HeaderValue::from_static("application/json"));
    headers.insert(AUTHORIZATION, HeaderValue::from_str(token).unwrap());

    let rate_limiter = RateLimiter::builder()
        .max(300)
        .refill(300)
        .interval(time::Duration::from_secs(60 * 15))
        .initial(300)
        .build();

    TwitterFetcher {
        tag: format!("%23{}", tag),
        from_date,
        end_date,
        cli: reqwest::blocking::Client::new(),
        headers,
        rate_limiter,
    }
}

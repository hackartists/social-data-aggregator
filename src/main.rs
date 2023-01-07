use std::env;

mod fetchers {
    pub mod twitter_fetcher;
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let token = env::var("TWITTER_TOKEN").unwrap();
    let keyword = "dao";

    let f = fetchers::twitter_fetcher::new(token.as_str(), keyword, 202104, 202301);
    f.start();

    Ok(())
}

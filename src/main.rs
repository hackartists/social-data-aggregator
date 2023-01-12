use std::env;

use futures::executor::block_on;

mod fetchers {
    pub mod twitter_fetcher;
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let token = env::var("TWITTER_TOKEN").unwrap();
    let keyword = "dao";

    let f = fetchers::twitter_fetcher::new(token.as_str(), keyword, 202201, 202301);
    block_on(f.start());

    Ok(())
}

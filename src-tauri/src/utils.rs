#[tauri::command]
pub async fn is_online() -> bool {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(3))
        .build()
        .unwrap();
    client
        .get("https://www.gstatic.com/generate_204")
        .send()
        .await
        .map(|r| r.status().as_u16() == 204)
        .unwrap_or(false)
}
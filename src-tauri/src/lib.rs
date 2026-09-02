mod counter;

use counter::my_custom_command;

#[tauri::command]
fn login(username: &str, password: &str) {
    println!("Vous voulez vous connecter {} et {}", username, password);
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![my_custom_command, login])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

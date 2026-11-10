<?php
// Telegram webhook relay (keithnah.com/tg/hook.php).
// Telegram cannot use the Apps Script web app directly (it answers with a redirect, so Telegram keeps
// retrying). This file answers Telegram at once with 200, then passes the update on to the Apps Script,
// which checks the secret, answers the button and does the work. It holds no token or secret itself:
// it forwards the X-Telegram-Bot-Api-Secret-Token header that Telegram sends, and the script checks it.
header('Content-Type: text/plain');
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { http_response_code(405); exit('POST only'); }
$body = file_get_contents('php://input');
$secret = $_SERVER['HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN'] ?? '';
if ($body === '' || strlen($body) > 100000 || $secret === '' || !preg_match('/^[A-Za-z0-9_-]{8,256}$/', $secret)) { http_response_code(200); exit('ignored'); }
$ep = '';
$lt = @file_get_contents(__DIR__ . '/../lead-tracker.js');
if ($lt && preg_match("/LEADS_ENDPOINT = '([^']+)'/", $lt, $m)) $ep = $m[1];
// answer Telegram now, then forward
http_response_code(200);
echo 'ok';
if (function_exists('fastcgi_finish_request')) { fastcgi_finish_request(); }
elseif (function_exists('litespeed_finish_request')) { litespeed_finish_request(); }
else { header('Content-Length: 2'); header('Connection: close'); @ob_end_flush(); flush(); }
ignore_user_abort(true);
if ($ep && function_exists('curl_init')) {
  $c = curl_init($ep . '?tg=' . rawurlencode($secret));
  curl_setopt_array($c, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => $body, CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => false, CURLOPT_TIMEOUT => 30]);
  @curl_exec($c);
}

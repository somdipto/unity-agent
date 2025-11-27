using System;
using System.Net;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;

public class WebSocketServer : MonoBehaviour
{
    private HttpListener httpListener;
    private CancellationTokenSource cancellationToken;
    
    [SerializeField] private int port = 8080;
    
    async void Start()
    {
        await StartServer();
    }
    
    async Task StartServer()
    {
        httpListener = new HttpListener();
        httpListener.Prefixes.Add($"http://localhost:{port}/");
        httpListener.Start();
        
        cancellationToken = new CancellationTokenSource();
        
        Debug.Log($"WebSocket server started on port {port}");
        
        while (!cancellationToken.Token.IsCancellationRequested)
        {
            var context = await httpListener.GetContextAsync();
            if (context.Request.IsWebSocketRequest)
            {
                _ = HandleWebSocketConnection(context);
            }
        }
    }
    
    async Task HandleWebSocketConnection(HttpListenerContext context)
    {
        var wsContext = await context.AcceptWebSocketAsync(null);
        var webSocket = wsContext.WebSocket;
        
        var buffer = new byte[1024 * 4];
        
        while (webSocket.State == WebSocketState.Open)
        {
            try
            {
                // Send game state
                var gameState = GetGameState();
                var stateJson = JsonConvert.SerializeObject(gameState);
                var stateBytes = Encoding.UTF8.GetBytes(stateJson);
                
                await webSocket.SendAsync(
                    new ArraySegment<byte>(stateBytes),
                    WebSocketMessageType.Text,
                    true,
                    cancellationToken.Token
                );
                
                // Receive actions
                var result = await webSocket.ReceiveAsync(
                    new ArraySegment<byte>(buffer),
                    cancellationToken.Token
                );
                
                if (result.MessageType == WebSocketMessageType.Text)
                {
                    var actionJson = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    ProcessAction(actionJson);
                }
                
                await Task.Delay(100); // 10 FPS
            }
            catch (Exception e)
            {
                Debug.LogError($"WebSocket error: {e.Message}");
                break;
            }
        }
    }
    
    object GetGameState()
    {
        var player = FindObjectOfType<PlayerController>();
        return new
        {
            player_position = new float[] { 
                player.transform.position.x,
                player.transform.position.y,
                player.transform.position.z
            },
            health = player.GetComponent<PlayerHealth>()?.currentHealth ?? 100f,
            timestamp = Time.time
        };
    }
    
    void ProcessAction(string actionJson)
    {
        // Process received action
        Debug.Log($"Received action: {actionJson}");
    }
    
    void OnDestroy()
    {
        cancellationToken?.Cancel();
        httpListener?.Stop();
    }
}

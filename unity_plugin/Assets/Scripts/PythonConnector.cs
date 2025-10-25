using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using LitJson;  // We'll use LitJson for JSON parsing which is common in Unity

public class PythonConnector : MonoBehaviour
{
    [Header("Connection Settings")]
    public string ipAddress = "127.0.0.1";
    public int port = 8080;
    
    [Header("Game State Settings")]
    public bool sendPosition = true;
    public bool sendHealth = true;
    public bool sendCombatState = true;
    public bool sendObjectives = true;
    public bool sendAreaInfo = true;
    
    private TcpClient client;
    private NetworkStream stream;
    private bool isConnected = false;
    private Thread receiveThread;
    private Queue<string> messageQueue = new Queue<string>();
    private object lockObject = new object();
    
    // Game state data that will be sent to Python
    private Dictionary<string, object> gameStateData;
    
    void Start()
    {
        ConnectToPython();
        gameStateData = new Dictionary<string, object>();
        StartCoroutine(SendGameStatePeriodically());
    }
    
    void OnApplicationQuit()
    {
        Disconnect();
    }
    
    public void ConnectToPython()
    {
        try
        {
            client = new TcpClient();
            client.Connect(ipAddress, port);
            stream = client.GetStream();
            isConnected = true;
            
            // Start a thread to receive messages from Python
            receiveThread = new Thread(new ThreadStart(ReceiveMessages));
            receiveThread.IsBackground = true;
            receiveThread.Start();
            
            Debug.Log("Connected to Python agent at " + ipAddress + ":" + port);
        }
        catch (Exception e)
        {
            Debug.LogError("Failed to connect to Python agent: " + e.Message);
            isConnected = false;
        }
    }
    
    public void Disconnect()
    {
        isConnected = false;
        
        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Abort();
        }
        
        if (stream != null)
        {
            stream.Close();
        }
        
        if (client != null)
        {
            client.Close();
        }
    }
    
    private void ReceiveMessages()
    {
        while (isConnected && client != null && client.Connected)
        {
            try
            {
                if (stream.DataAvailable)
                {
                    byte[] buffer = new byte[4096];
                    int bytesRead = stream.Read(buffer, 0, buffer.Length);
                    
                    if (bytesRead > 0)
                    {
                        string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                        lock (lockObject)
                        {
                            messageQueue.Enqueue(message);
                        }
                    }
                }
                
                Thread.Sleep(10); // Small delay to prevent busy waiting
            }
            catch (Exception e)
            {
                Debug.LogError("Error receiving message from Python: " + e.Message);
                break;
            }
        }
    }
    
    public void SendToPython(string message)
    {
        if (!isConnected || stream == null)
        {
            Debug.LogWarning("Not connected to Python, cannot send message");
            return;
        }
        
        try
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            stream.Write(data, 0, data.Length);
            stream.Flush();
        }
        catch (Exception e)
        {
            Debug.LogError("Error sending message to Python: " + e.Message);
        }
    }
    
    private IEnumerator SendGameStatePeriodically()
    {
        while (true)
        {
            if (isConnected)
            {
                SendGameState();
            }
            yield return new WaitForSeconds(0.5f); // Send state every half second
        }
    }
    
    private void SendGameState()
    {
        gameStateData.Clear();
        
        // Gather game state information
        gameStateData["position"] = new float[] { 
            transform.position.x, 
            transform.position.y, 
            transform.position.z 
        };
        
        if (sendHealth)
        {
            // This assumes there's a PlayerHealth component or similar
            var playerHealth = FindObjectOfType<PlayerHealth>();
            if (playerHealth != null)
            {
                gameStateData["health"] = playerHealth.currentHealth;
            }
            else
            {
                gameStateData["health"] = 100; // default value if no health component found
            }
        }
        
        if (sendCombatState)
        {
            var combatManager = FindObjectOfType<CombatManager>();
            if (combatManager != null)
            {
                gameStateData["in_combat"] = combatManager.isInCombat;
            }
            else
            {
                gameStateData["in_combat"] = false;
            }
        }
        
        if (sendObjectives)
        {
            var objectiveTracker = FindObjectOfType<ObjectiveTracker>();
            if (objectiveTracker != null)
            {
                gameStateData["current_objective"] = objectiveTracker.GetCurrentObjective();
                gameStateData["level_progress"] = objectiveTracker.GetProgress();
            }
            else
            {
                gameStateData["current_objective"] = null;
                gameStateData["level_progress"] = 0.0f;
            }
        }
        
        if (sendAreaInfo)
        {
            gameStateData["current_area"] = GetAreaName();
            gameStateData["puzzle_active"] = IsInPuzzleArea();
        }
        
        gameStateData["time_in_level"] = Time.time;
        gameStateData["is_dead"] = IsPlayerDead();
        
        // Convert to JSON and send
        string json = JsonMapper.ToJson(gameStateData);
        
        // Create a message wrapper
        var messageWrapper = new Dictionary<string, object>
        {
            {"type", "game_state_update"},
            {"agent_id", GetAgentId()},
            {"data", gameStateData},
            {"timestamp", DateTime.UtcNow.ToString("o")}
        };
        
        string message = JsonMapper.ToJson(messageWrapper);
        SendToPython(message);
    }
    
    private string GetAreaName()
    {
        // Implement based on your game's area system
        // This could be based on scene name, trigger volumes, etc.
        return SceneManager.GetActiveScene().name;
    }
    
    private bool IsInPuzzleArea()
    {
        // Implement based on your game's puzzle detection system
        var puzzleTrigger = Physics.OverlapSphere(transform.position, 5.0f);
        foreach (var trigger in puzzleTrigger)
        {
            if (trigger.CompareTag("PuzzleArea"))
            {
                return true;
            }
        }
        return false;
    }
    
    private bool IsPlayerDead()
    {
        var playerHealth = FindObjectOfType<PlayerHealth>();
        return playerHealth != null && playerHealth.currentHealth <= 0;
    }
    
    private int GetAgentId()
    {
        // This could be set by the Python system when the agent connects
        // For now, returning a default value
        return 0;
    }
    
    void Update()
    {
        // Process received messages
        lock (lockObject)
        {
            while (messageQueue.Count > 0)
            {
                string message = messageQueue.Dequeue();
                ProcessMessage(message);
            }
        }
    }
    
    private void ProcessMessage(string message)
    {
        try
        {
            var parsed = JsonMapper.ToObject(message);
            
            if (parsed.ContainsKey("type"))
            {
                string type = parsed["type"].ToString();
                
                switch (type)
                {
                    case "action":
                        ProcessActionMessage(parsed);
                        break;
                    case "get_state":
                        ProcessGetStateMessage(parsed);
                        break;
                    case "set_setting":
                        ProcessSetSettingMessage(parsed);
                        break;
                    case "get_level_data":
                        ProcessGetLevelDataMessage(parsed);
                        break;
                    default:
                        Debug.Log("Unknown message type: " + type);
                        break;
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError("Error processing message: " + e.Message);
        }
    }
    
    private void ProcessActionMessage(JsonData message)
    {
        if (message.ContainsKey("data"))
        {
            JsonData data = message["data"];
            if (data.ContainsKey("action"))
            {
                string action = data["action"].ToString();
                int agentId = (int)data["agent_id"];
                
                // Execute the action based on the agent ID
                ExecuteAction(agentId, action);
            }
        }
    }
    
    private void ProcessGetStateMessage(JsonData message)
    {
        if (message.ContainsKey("agent_id"))
        {
            int agentId = (int)message["agent_id"];
            
            // Send the current game state for this agent
            SendGameState();
        }
    }
    
    private void ProcessSetSettingMessage(JsonData message)
    {
        if (message.ContainsKey("data"))
        {
            JsonData data = message["data"];
            if (data.ContainsKey("setting") && data.ContainsKey("value"))
            {
                string setting = data["setting"].ToString();
                string value = data["value"].ToString();
                
                // Apply the setting change
                ApplyGameSetting(setting, value);
            }
        }
    }
    
    private void ProcessGetLevelDataMessage(JsonData message)
    {
        if (message.ContainsKey("data"))
        {
            JsonData data = message["data"];
            if (data.ContainsKey("level_name"))
            {
                string levelName = data["level_name"].ToString();
                
                // Send level data back to Python
                SendLevelData(levelName);
            }
        }
    }
    
    private void ExecuteAction(int agentId, string action)
    {
        // Based on the action string, execute the corresponding game action
        switch (action)
        {
            case "move_forward":
                MoveForward();
                break;
            case "move_backward":
                MoveBackward();
                break;
            case "jump":
                Jump();
                break;
            case "crouch":
                Crouch();
                break;
            case "attack":
                Attack();
                break;
            case "defend":
                Defend();
                break;
            case "interact":
                Interact();
                break;
            case "look_around":
                LookAround();
                break;
            default:
                Debug.LogWarning("Unknown action: " + action);
                break;
        }
    }
    
    private void MoveForward()
    {
        // Implement move forward logic for the agent
        transform.Translate(Vector3.forward * Time.deltaTime * 5.0f);
    }
    
    private void MoveBackward()
    {
        // Implement move backward logic for the agent
        transform.Translate(Vector3.back * Time.deltaTime * 5.0f);
    }
    
    private void Jump()
    {
        // Implement jump logic for the agent
        // This requires a Rigidbody and proper physics setup
        var rb = GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.AddForce(Vector3.up * 500.0f);
        }
    }
    
    private void Crouch()
    {
        // Implement crouch logic for the agent
        Debug.Log("Crouching...");
    }
    
    private void Attack()
    {
        // Implement attack logic for the agent
        Debug.Log("Attacking...");
    }
    
    private void Defend()
    {
        // Implement defend logic for the agent
        Debug.Log("Defending...");
    }
    
    private void Interact()
    {
        // Implement interaction logic for the agent
        Debug.Log("Interacting...");
    }
    
    private void LookAround()
    {
        // Implement look around logic for the agent
        // Maybe change rotation randomly to look around
        transform.Rotate(Vector3.up, UnityEngine.Random.Range(-30, 30));
    }
    
    private void ApplyGameSetting(string setting, string value)
    {
        // Apply changes to game settings based on the setting name and value
        switch (setting)
        {
            case "rendering_quality":
                QualitySettings.SetQualityLevel(value == "high" ? 3 : 0); // High or Low
                break;
            case "ui_visible":
                // Find UI elements and enable/disable them
                var canvasObjects = FindObjectsOfType<Canvas>();
                foreach (var canvas in canvasObjects)
                {
                    canvas.gameObject.SetActive(value == "true");
                }
                break;
            case "player_input_disabled":
                // Disable player input based on value
                var playerInput = FindObjectOfType<PlayerInput>();
                if (playerInput != null)
                {
                    playerInput.enabled = !(value == "true");
                }
                break;
            default:
                Debug.LogWarning("Unknown setting: " + setting);
                break;
        }
    }
    
    private void SendLevelData(string levelName)
    {
        var levelData = new Dictionary<string, object>
        {
            {"level_name", levelName},
            {"bounds", new Dictionary<string, object>
                {
                    {"min", new float[] {-10, -10, -10}},
                    {"max", new float[] {10, 10, 10}}
                }
            },
            {"obstacles", new List<object>()},
            {"collectibles", new List<object>()},
            {"enemies", new List<object>()},
            {"checkpoints", new List<object>()}
        };
        
        // In a real implementation, populate these lists with actual level info
        PopulateLevelData(levelData, levelName);
        
        // Create a message to send back
        var response = new Dictionary<string, object>
        {
            {"type", "level_data_response"},
            {"data", levelData},
            {"timestamp", DateTime.UtcNow.ToString("o")}
        };
        
        string message = JsonMapper.ToJson(response);
        SendToPython(message);
    }
    
    private void PopulateLevelData(Dictionary<string, object> levelData, string levelName)
    {
        // In a real implementation, scan the level and populate with actual data
        // For now, just adding placeholder data
        var obstacles = (List<object>)levelData["obstacles"];
        var collectibles = (List<object>)levelData["collectibles"];
        var enemies = (List<object>)levelData["enemies"];
        var checkpoints = (List<object>)levelData["checkpoints"];
        
        // This would actually scan the scene for these objects
        // For example:
        // foreach (var obstacle in FindObjectsOfType<Obstacle>()) {
        //     obstacles.Add(new Dictionary<string, object> {
        //         {"position", new float[] {obstacle.transform.position.x, obstacle.transform.position.y, obstacle.transform.position.z}},
        //         {"type", obstacle.GetType().Name}
        //     });
        // }
    }
}
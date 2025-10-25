using UnityEngine;
using UnityEngine.SceneManagement;

public class ObjectiveTracker : MonoBehaviour
{
    [Header("Objectives")]
    public string[] objectives;
    public int currentObjectiveIndex = 0;
    
    [Header("Progress Tracking")]
    public float levelProgress = 0.0f;
    public bool[] objectiveCompleted;

    void Start()
    {
        objectiveCompleted = new bool[objectives.Length];
        for (int i = 0; i < objectiveCompleted.Length; i++)
        {
            objectiveCompleted[i] = false;
        }
    }

    public void CompleteObjective(int index)
    {
        if (index >= 0 && index < objectiveCompleted.Length)
        {
            objectiveCompleted[index] = true;
            currentObjectiveIndex = index + 1;
            UpdateLevelProgress();
        }
    }

    public string GetCurrentObjective()
    {
        if (currentObjectiveIndex >= 0 && currentObjectiveIndex < objectives.Length)
        {
            return objectives[currentObjectiveIndex];
        }
        return "No active objective";
    }

    public float GetProgress()
    {
        int completed = 0;
        for (int i = 0; i < objectiveCompleted.Length; i++)
        {
            if (objectiveCompleted[i]) completed++;
        }
        return (float)completed / objectiveCompleted.Length;
    }

    private void UpdateLevelProgress()
    {
        levelProgress = GetProgress();
    }

    // For testing
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.O))
        {
            if (currentObjectiveIndex < objectives.Length)
            {
                CompleteObjective(currentObjectiveIndex);
            }
        }
    }
}
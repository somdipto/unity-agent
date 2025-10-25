using UnityEngine;

public class CombatManager : MonoBehaviour
{
    [Header("Combat Settings")]
    public bool isInCombat = false;
    public float combatRange = 10.0f;
    public GameObject[] enemiesInRange;

    [Header("Combat State")]
    public bool canAttack = true;
    public float attackCooldown = 1.0f;
    private float lastAttackTime = 0.0f;

    void Start()
    {
        enemiesInRange = new GameObject[0];
    }

    void Update()
    {
        UpdateCombatState();
        
        if (Input.GetKeyDown(KeyCode.C))
        {
            ToggleCombatDebug();
        }
    }

    void UpdateCombatState()
    {
        // Find enemies in range
        Collider[] colliders = Physics.OverlapSphere(transform.position, combatRange);
        System.Collections.Generic.List<GameObject> tempEnemies = new System.Collections.Generic.List<GameObject>();
        
        foreach (Collider col in colliders)
        {
            if (col.CompareTag("Enemy"))
            {
                tempEnemies.Add(col.gameObject);
            }
        }
        
        enemiesInRange = tempEnemies.ToArray();
        isInCombat = enemiesInRange.Length > 0;
    }

    public bool CanAttack()
    {
        return canAttack && (Time.time - lastAttackTime) > attackCooldown;
    }

    public void PerformAttack()
    {
        if (CanAttack())
        {
            lastAttackTime = Time.time;
            // Perform attack animation, damage calculation, etc.
            Debug.Log("Performing attack!");
        }
    }

    private void ToggleCombatDebug()
    {
        isInCombat = !isInCombat;
        Debug.Log("Combat state toggled: " + isInCombat);
    }

    // Visualize combat range in the editor
    void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, combatRange);
    }
}
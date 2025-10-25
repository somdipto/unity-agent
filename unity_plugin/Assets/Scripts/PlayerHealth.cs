using UnityEngine;

public class PlayerHealth : MonoBehaviour
{
    [Header("Health Settings")]
    public float maxHealth = 100f;
    public float currentHealth;

    [Header("Damage Effects")]
    public GameObject damageEffect;
    public AudioClip damageSound;

    void Start()
    {
        currentHealth = maxHealth;
    }

    public void TakeDamage(float damage)
    {
        currentHealth -= damage;
        currentHealth = Mathf.Clamp(currentHealth, 0, maxHealth);

        // Play damage effect
        if (damageEffect != null)
        {
            Instantiate(damageEffect, transform.position, Quaternion.identity);
        }

        if (damageSound != null)
        {
            AudioSource.PlayClipAtPoint(damageSound, transform.position);
        }

        // Check if player died
        if (currentHealth <= 0)
        {
            Die();
        }
    }

    public void Heal(float amount)
    {
        currentHealth += amount;
        currentHealth = Mathf.Clamp(currentHealth, 0, maxHealth);
    }

    void Die()
    {
        // Handle player death
        Debug.Log("Player died!");
        
        // Disable player controls
        // Trigger death animation
        // Maybe respawn or end game
        
        // For now, just disable the player controller
        var playerController = GetComponent<PlayerController>();
        if (playerController != null)
        {
            playerController.enabled = false;
        }
    }
    
    // For testing purposes
    void Update()
    {
        // Simulate taking damage if health > 0 and space is pressed
        if (Input.GetKeyDown(KeyCode.Space) && currentHealth > 0)
        {
            TakeDamage(20f);
            Debug.Log("Health: " + currentHealth);
        }
        
        // Simulate healing if health < max and H is pressed
        if (Input.GetKeyDown(KeyCode.H) && currentHealth < maxHealth)
        {
            Heal(20f);
            Debug.Log("Health: " + currentHealth);
        }
    }
}
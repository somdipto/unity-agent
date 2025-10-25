using UnityEngine;

public class PlayerInput : MonoBehaviour
{
    [Header("Movement Settings")]
    public float moveSpeed = 5.0f;
    public float turnSpeed = 50.0f;

    [Header("Jump Settings")]
    public float jumpForce = 7.0f;
    private bool isGrounded = true;

    private Rigidbody rb;
    private Camera playerCamera;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        playerCamera = Camera.main;
    }

    void Update()
    {
        // Only allow input if enabled
        if (this.enabled)
        {
            HandleMovement();
            HandleJump();
            HandleLook();
        }
    }

    void HandleMovement()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        Vector3 movement = new Vector3(horizontal, 0, vertical);
        movement = movement.normalized * moveSpeed * Time.deltaTime;

        // Move relative to the camera view
        if (playerCamera != null)
        {
            movement = playerCamera.transform.TransformDirection(movement);
            movement.y = 0; // Keep movement on XZ plane
        }

        transform.Translate(movement);
    }

    void HandleJump()
    {
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
            isGrounded = false;
        }
    }

    void HandleLook()
    {
        float mouseX = Input.GetAxis("Mouse X");
        float mouseY = Input.GetAxis("Mouse Y");

        // Rotate player based on mouse input
        transform.Rotate(0, mouseX * turnSpeed * Time.deltaTime, 0);
    }

    void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = true;
        }
    }

    void OnCollisionExit(Collision collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = false;
        }
    }
}
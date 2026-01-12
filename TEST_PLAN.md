# Test Plan for gpt-buddy

## Overview
This document outlines the comprehensive test strategy for the gpt-buddy voice assistant application. The current codebase has no existing test infrastructure, making it critical to establish a solid testing foundation.

## Test Infrastructure Requirements

### Tools & Frameworks
- **pytest** - Primary testing framework
- **pytest-cov** - Code coverage reporting
- **pytest-mock** - Mocking support
- **unittest.mock** - Standard library mocking
- **pytest-asyncio** - If async refactoring is done
- **freezegun** - Time-based testing

### Directory Structure
```
gpt-buddy/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_helpers.py
│   │   ├── test_gpt.py
│   │   ├── test_apprise_sender.py
│   │   ├── test_scheduled_image.py
│   │   └── test_main.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_conversation_flow.py
│   │   └── test_image_generation.py
│   └── fixtures/
│       ├── test_audio.mp3
│       ├── test_image.png
│       └── mock_responses.json
```

## Critical Unit Tests (Priority 1)

### helpers.py Tests

#### test_play_audio()
**Purpose:** Verify audio playback functionality  
**Test Cases:**
- Valid audio file plays successfully
- Player is created with correct path
- Function waits for playback completion
- Handles missing audio file gracefully
- Handles corrupted audio file

**Mocks Required:**
- `vlc.MediaPlayer`
- `time.sleep`

#### test_display_image()
**Purpose:** Verify image display on framebuffer  
**Test Cases:**
- Kills existing fbi process
- Launches fbi with correct parameters
- Handles missing image file
- Prevents command injection via malicious paths
- Handles subprocess errors

**Mocks Required:**
- `subprocess.call`

**Security Tests:**
- Path traversal attempts: `../../etc/passwd`
- Command injection: `image.png; rm -rf /`
- Special characters in paths

### gpt.py Tests

#### test_get_assistant()
**Purpose:** Verify assistant retrieval  
**Test Cases:**
- Successfully retrieves assistant with valid ID
- Returns correct assistant object
- Handles invalid assistant ID
- Handles API connection errors
- Logs assistant information

**Mocks Required:**
- `openai_client.beta.assistants.retrieve()`

#### test_whisper_text_to_speech()
**Purpose:** Verify text-to-speech generation  
**Test Cases:**
- Creates speech file successfully
- Uses correct model and voice
- Plays generated audio
- Handles empty text input
- Handles very long text input
- Handles API errors

**Mocks Required:**
- `openai_client.audio.speech.create()`
- `helpers.play_audio()`

#### test_generate_chatgpt_image()
**Purpose:** Verify DALL-E image generation  
**Test Cases:**
- Generates image with correct prompt
- Downloads image successfully
- Resizes image to 800x480
- Displays resized image
- Handles API errors
- Handles network timeouts
- Handles invalid image data

**Mocks Required:**
- `openai_client.images.generate()`
- `requests.get()`
- `PIL.Image.open()`
- `helpers.display_image()`

#### test_send_to_assistant()
**Purpose:** Verify complete assistant interaction  
**Test Cases:**
- Sends message to assistant
- Creates run successfully
- Polls for completion correctly
- Returns assistant response
- Handles timeout after 10 seconds
- Starts image generation thread
- Calls text-to-speech when enabled
- Skips text-to-speech when disabled
- Handles empty responses
- Handles API errors during run

**Mocks Required:**
- `openai_client.beta.threads.messages.create()`
- `openai_client.beta.threads.runs.create()`
- `openai_client.beta.threads.runs.retrieve()`
- `openai_client.beta.threads.messages.list()`
- `threading.Thread`
- `time.sleep`

### apprise_sender.py Tests

#### test_send()
**Purpose:** Verify notification sending  
**Test Cases:**
- Sends notification with configured services
- Includes title, message, and attachment
- Handles empty service list gracefully
- Handles missing attachment file
- Handles invalid service URLs
- Logs sending activity

**Mocks Required:**
- `apprise.Apprise`

### scheduled_image.py Tests

#### test_scheduled_image()
**Purpose:** Verify scheduled image generation  
**Test Cases:**
- Reads thread ID from file
- Calls assistant with scheduled prompt
- Disables text-to-speech
- Handles missing thread file
- Handles invalid thread ID
- Handles API errors

**Mocks Required:**
- `gpt.get_assistant()`
- `gpt.send_to_assistant()`
- File system operations

## Integration Tests (Priority 2)

### test_conversation_flow.py

#### test_hotword_to_response_flow()
**Purpose:** Test complete interaction from hotword to response  
**Scenario:**
1. Wait for hotword
2. Detect hotword
3. Listen for speech
4. Recognize speech
5. Send to assistant
6. Get response
7. Play response audio
8. Generate image
9. Return to hotword waiting

**Mocks:** All external APIs, hardware interfaces

#### test_cancel_conversation()
**Purpose:** Test conversation cancellation  
**Scenario:**
1. Detect hotword
2. Recognize cancel phrase
3. Play acknowledgment
4. Return to hotword waiting
5. No API calls made

### test_image_generation.py

#### test_dalle_image_generation()
**Purpose:** Test DALL-E image generation flow  
**Scenario:**
1. Trigger conversation
2. Get assistant response
3. Generate DALL-E image in background
4. Download and resize image
5. Display on screen

#### test_stable_diffusion_generation()
**Purpose:** Test Stable Diffusion generation  
**Scenario:**
1. Detect "make image about" command
2. Extract prompt
3. Call Stable Diffusion API
4. Save and display image
5. Store prompt for "make another"

#### test_send_image_to_telegram()
**Purpose:** Test image sending  
**Scenario:**
1. Generate image
2. Detect "send" command
3. Send via Apprise
4. Save to saved_images directory

## Edge Case Tests (Priority 2)

### test_empty_directories()
**Test Cases:**
- Empty saved_images/ directory
- Missing audio/ directory
- Missing assistant_images/ directory

### test_file_system_errors()
**Test Cases:**
- Read-only file system
- Disk full
- Permission denied

### test_network_failures()
**Test Cases:**
- OpenAI API unreachable
- Stable Diffusion API unreachable
- Intermittent network errors
- Slow network (timeouts)

### test_api_errors()
**Test Cases:**
- Rate limiting (429 errors)
- Authentication errors (401)
- Invalid requests (400)
- Server errors (500)

### test_concurrency()
**Test Cases:**
- Rapid hotword triggers
- Multiple audio playback requests
- Image generation while playing audio
- Thread synchronization issues

### test_resource_limits()
**Test Cases:**
- Very long speech input
- Very long assistant response
- Large image files
- Many saved images

## Security Tests (Priority 1)

### test_command_injection()
**Test Cases:**
- Malicious image paths in display_image()
- SQL injection attempts (if database added)
- Path traversal attempts
- Shell metacharacters in filenames

### test_input_validation()
**Test Cases:**
- Malicious speech input
- Extremely long prompts
- Special characters in prompts
- Unicode edge cases

### test_api_key_handling()
**Test Cases:**
- Missing API keys
- Invalid API keys
- API key exposure in logs
- API key exposure in errors

## Performance Tests (Priority 3)

### test_response_times()
**Metrics:**
- Hotword detection latency
- Speech recognition time
- Assistant response time
- Image generation time
- Total end-to-end time

### test_resource_usage()
**Metrics:**
- Memory usage over time
- CPU usage during operations
- Thread count
- File descriptor usage

## Test Implementation Priority

### Phase 1: Critical Unit Tests (Week 1)
1. helpers.py - test_display_image (security critical)
2. helpers.py - test_play_audio
3. gpt.py - test_send_to_assistant
4. gpt.py - test_generate_chatgpt_image

### Phase 2: Supporting Unit Tests (Week 2)
5. gpt.py - test_whisper_text_to_speech
6. gpt.py - test_get_assistant
7. apprise_sender.py - test_send
8. scheduled_image.py - test_scheduled_image

### Phase 3: Integration Tests (Week 3)
9. test_conversation_flow
10. test_image_generation
11. test_cancel_conversation

### Phase 4: Edge Cases & Security (Week 4)
12. Security tests (command injection)
13. Edge case tests (empty directories, errors)
14. Network failure tests

### Phase 5: Performance & Monitoring (Week 5)
15. Performance tests
16. Resource usage tests
17. Load tests

## Test Coverage Goals

- **Overall Coverage:** >80%
- **helpers.py:** >90% (security critical)
- **gpt.py:** >85% (core functionality)
- **apprise_sender.py:** >80%
- **scheduled_image.py:** >80%
- **main.py:** >70% (difficult to test, should be refactored)

## Continuous Integration

### Pre-commit Hooks
- Run unit tests
- Check code coverage
- Run linting (black, flake8)
- Run security checks (bandit)

### CI Pipeline
- Run all tests on every commit
- Generate coverage reports
- Run security scans
- Check for dependency vulnerabilities

## Refactoring Recommendations for Testability

### main.py
- Extract state machine logic to separate class
- Extract command handlers to separate functions
- Reduce coupling with hardware interfaces
- Add dependency injection for easier mocking

### gpt.py
- Separate HTTP logic from business logic
- Make thread management more explicit
- Add interfaces for external dependencies

### helpers.py
- Replace subprocess calls with proper process management
- Add abstractions for audio/video hardware

## Mock Data Requirements

### Audio Files
- Short audio clip (1-2 seconds)
- Long audio clip (10+ seconds)
- Corrupted audio file
- Empty audio file

### Image Files
- Valid PNG image
- Valid JPG image
- Corrupted image file
- Very large image
- Very small image

### API Responses
- Successful assistant responses
- Error responses (rate limit, auth, etc.)
- Timeout scenarios
- Malformed responses

## Success Criteria

✅ All critical unit tests passing  
✅ >80% code coverage achieved  
✅ Security tests prevent command injection  
✅ Integration tests verify main flows  
✅ CI/CD pipeline running tests automatically  
✅ Documentation for running tests  
✅ Mock fixtures available for all external dependencies  
✅ Edge cases handled gracefully  
✅ Performance benchmarks established  

## Next Steps

1. Set up pytest and testing dependencies
2. Create test directory structure
3. Implement shared fixtures in conftest.py
4. Start with helpers.py tests (highest security risk)
5. Implement gpt.py tests (core functionality)
6. Add integration tests
7. Establish CI/CD pipeline
8. Document testing procedures

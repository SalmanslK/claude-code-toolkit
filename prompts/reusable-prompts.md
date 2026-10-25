# Reusable Prompts for C# Software Engineers

> **Total Prompts: 106** | One collection, organized by category. Replaces the earlier Compact (52) and Top 100 sets.

---

## Contents

- 📋 Issue & Problem Resolution (1-5)
- 🔍 Code Review & Audit (6-15)
- 📝 Documentation (16-28)
- 📊 Azure DevOps & Task Management (29-38)
- 🏗️ Architecture & Design (39-50)
- 🧪 Testing (51-62)
- 🔧 Implementation & Coding (63-75)
- 🗄️ Database & Migrations (76-82)
- 🐛 Debugging & Troubleshooting (83-88)
- 📦 Dependency & Package Management (89-91)
- 🚀 Deployment & DevOps (92-95)
- 💬 Communication (96-100)
- 🔄 Quick Actions (101-106)
- 🔄 Quick Reference - Common Patterns

---

## 📋 Issue & Problem Resolution (1-5)

### 1. Issue Summary for Stakeholders
```
Write a short summary for the issue below, formatted for business stakeholders:
- The Issue: What problem we were facing
- Root Cause: The findings/reason behind it
- Impact Areas: Before and after the changes (side effects, affected components)
- Solution: The suggested/implemented fix
```

### 2. Bug Investigation
```
Analyze this error/exception and:
1. Identify the root cause
2. List all affected code paths
3. Suggest a fix with minimal side effects
4. Recommend tests to prevent regression
```

### 3. Production Incident Post-Mortem
```
Based on this incident, create a post-mortem document including:
- Timeline of events
- Root cause analysis
- Impact assessment
- Resolution steps taken
- Preventive measures for the future
```

### 4. Regression Analysis
```
This bug was introduced recently. Help me:
1. Identify when the regression was introduced
2. Determine which commit/change caused it
3. Analyze why it wasn't caught by existing tests
4. Suggest fixes and test improvements
```

### 5. Impact Analysis
```
Analyze the impact of changing [COMPONENT/METHOD/CLASS]:
- Direct dependencies affected
- Indirect ripple effects
- Breaking changes for consumers
- Required test updates
- Documentation changes needed
```

---

## 🔍 Code Review & Audit (6-15)

### 6. Audit Unstaged Changes
```
You are a Software Architect reviewing my unstaged changes. Analyze them for:
- Code quality and adherence to SOLID principles
- Potential bugs or edge cases
- Performance implications
- Security concerns
- Test coverage gaps

At the end, state whether you approve the changes or have recommendations.
```

### 7. Audit Branch Changes
```
You are a Software Architect reviewing all changes in this branch. Analyze:
- Overall design decisions
- Breaking changes
- Backward compatibility
- Adherence to architecture patterns (Clean Architecture, CQRS)
- Missing validations or error handling

At the end, state whether you approve the changes or have recommendations.
```

### 8. Quick Code Review
```
Review this code for:
1. Bugs and edge cases
2. Naming conventions
3. SOLID principle violations
4. Opportunities for refactoring
```

### 9. Security Audit
```
Audit this code/changes for security vulnerabilities:
- SQL injection
- XSS vulnerabilities
- Insecure deserialization
- Sensitive data exposure
- Authentication/authorization gaps
```

### 10. PR Review Assistance
```
Review this pull request and provide:
- Summary of changes
- Potential issues or concerns
- Suggestions for improvement
- Approval recommendation
```

### 11. SOLID Principles Check
```
Analyze this code against SOLID principles:
- Single Responsibility: Does each class have one reason to change?
- Open/Closed: Is it open for extension, closed for modification?
- Liskov Substitution: Can derived classes substitute base classes?
- Interface Segregation: Are interfaces focused and minimal?
- Dependency Inversion: Are dependencies on abstractions?

Provide specific violations and fixes.
```

### 12. Thread Safety Review
```
Review this code for thread safety issues:
- Race conditions
- Deadlock potential
- Shared state mutations
- Proper use of locks/synchronization
- Async/await pitfalls

Recommend thread-safe alternatives.
```

### 13. Memory Leak Detection
```
Analyze this code for potential memory leaks:
- Undisposed resources
- Event handler subscriptions
- Static references holding objects
- Large object allocations
- Circular references

Suggest fixes for each issue found.
```

### 14. API Contract Review
```
Review this API endpoint for:
- RESTful conventions compliance
- Request/response model design
- Error response consistency
- Versioning considerations
- Documentation completeness
```

### 15. Dependency Analysis
```
Analyze the dependencies in this code:
- Are dependencies properly injected?
- Are there hidden dependencies?
- Is the dependency graph too deep?
- Are there circular dependencies?
- Can any dependencies be removed?
```

---

## 📝 Documentation (16-28)

### 16. Update Existing Documentation
```
Based on the changes made, identify which existing documentation needs to be updated. List specific files and sections requiring changes.
```

### 17. Update API Documentation & Postman
```
Update the API Documentation and Postman collection to reflect the current changes. Ensure endpoints, request/response schemas, and examples are accurate.
```

### 18. Generate Technical Documentation
```
Create technical documentation for this feature/module including:
- Overview and purpose
- Architecture decisions
- API contracts
- Data flow diagrams
- Configuration requirements
```

### 19. Create Change Summary
```
Based on all changes made so far on this branch and our conversation context:
1. Create a detailed summary markdown file for all changes in the docs folder
2. Include: files modified, reason for changes, and any breaking changes
```

### 20. Generate Rules/Guidelines
```
Based on all changes made on this branch and our conversation context:
1. Create a set of verification rules to ensure these changes remain intact in future implementations
2. Save as a markdown file in the docs folder
```

### 21. Create README Section
```
Generate a README section for this feature/module covering:
- What it does
- How to use it
- Configuration options
- Example usage
```

### 22. Document Code Inline
```
Add XML documentation comments to this code including:
- Summary descriptions
- Parameter explanations
- Return value documentation
- Example usage where appropriate
```

### 23. Create Architecture Decision Record (ADR)
```
Create an ADR for this decision:
- Title: Short descriptive title
- Status: Proposed/Accepted/Deprecated
- Context: Why is this decision needed?
- Decision: What was decided?
- Consequences: What are the implications?
- Alternatives Considered: What else was evaluated?
```

### 24. Generate OpenAPI Specification
```
Generate OpenAPI/Swagger specification for this API including:
- Endpoint definitions
- Request/response schemas
- Authentication requirements
- Error responses
- Example values
```

### 25. Create Troubleshooting Guide
```
Create a troubleshooting guide for this feature:
- Common issues and solutions
- Error codes and meanings
- Diagnostic steps
- Log locations and what to look for
- Escalation procedures
```

### 26. Document Environment Setup
```
Create environment setup documentation:
- Prerequisites
- Installation steps
- Configuration settings
- Verification steps
- Common setup issues
```

### 27. Create Runbook
```
Create an operational runbook for this service:
- Health check procedures
- Restart procedures
- Scaling guidelines
- Backup/restore steps
- Emergency contacts
```

### 28. Generate Code Comments Strategy
```
Suggest a commenting strategy for this codebase:
- What to comment
- What not to comment
- Documentation comment standards
- TODO/FIXME conventions
- Examples of good vs bad comments
```

---

## 📊 Azure DevOps & Task Management (29-38)

### 29. Suggest Tasks for Branch Changes
```
Suggest Azure Board tasks for all changes in this branch. Include:
- Task title
- Description
- Acceptance criteria
- Estimated effort
```

### 30. Generate Tasks from Work Period
```
Based on my work, chats, and commits from [START_DATE] to [END_DATE], identify the work completed and suggest Azure Board tasks to create for documentation purposes.
```

### 31. Create User Story
```
Create an Azure DevOps User Story for this feature:
- Title
- Description (As a... I want... So that...)
- Acceptance Criteria
- Tasks breakdown
```

### 32. Sprint Review Summary
```
Based on the commits and changes this sprint, create a summary for the sprint review including:
- Features completed
- Bugs fixed
- Technical debt addressed
- Carry-over items
```

### 33. Create Bug Work Item
```
Create an Azure DevOps Bug work item:
- Title (clear, searchable)
- Repro steps
- Expected vs actual behavior
- Severity and priority
- Environment details
- Suggested fix (if known)
```

### 34. Estimate Work Item
```
Estimate the effort for implementing this work item:
- Story points (using Fibonacci)
- Time estimate in hours
- Risk factors
- Dependencies
- Assumptions made
```

### 35. Sprint Planning Suggestions
```
Based on the backlog and team capacity, suggest:
- Which items to commit to this sprint
- Logical groupings of work
- Risk items that need spikes
- Dependencies to address first
```

### 36. Create Epic Breakdown
```
Break down this Epic into User Stories:
- Logical feature groupings
- MVP vs nice-to-have items
- Suggested sprint allocation
- Dependencies between stories
```

### 37. Retrospective Summary
```
Based on this sprint's work and issues encountered, create retrospective notes:
- What went well
- What could be improved
- Action items for next sprint
- Process improvements
```

### 38. Technical Debt Backlog Item
```
Create a technical debt work item:
- Problem description
- Business impact
- Technical approach
- Estimated effort
- Suggested priority
```

---

## 🏗️ Architecture & Design (39-50)

### 39. Design Review
```
Review this design/approach for:
- Scalability concerns
- Maintainability
- Adherence to Clean Architecture principles
- CQRS pattern compliance
- Potential bottlenecks
```

### 40. Suggest Architecture Improvements
```
Analyze the current implementation and suggest architectural improvements for:
- Better separation of concerns
- Reduced coupling
- Improved testability
- Enhanced performance
```

### 41. Create Technical Specification
```
Create a technical specification for implementing [FEATURE] including:
- High-level design
- Component interactions
- Database schema changes
- API contracts
- Migration strategy
```

### 42. Evaluate Design Options
```
Compare these design approaches and recommend the best option considering:
- Complexity
- Maintainability
- Performance
- Team expertise
- Time constraints
```

### 43. Design Pattern Recommendation
```
For this problem, recommend appropriate design patterns:
- Pattern name and description
- Why it fits this use case
- Implementation example
- Potential drawbacks
- Alternatives considered
```

### 44. Microservices Boundary Analysis
```
Analyze whether this feature should be:
- Part of existing service
- New microservice
- Shared library

Consider: domain boundaries, scaling needs, team ownership, data ownership.
```

### 45. Event-Driven Architecture Design
```
Design an event-driven solution for this feature:
- Events to publish
- Event schema
- Subscribers and their responsibilities
- Error handling and retry strategy
- Idempotency considerations
```

### 46. API Versioning Strategy
```
Recommend an API versioning strategy:
- Versioning method (URL, header, query string)
- Breaking vs non-breaking changes
- Deprecation policy
- Migration path for clients
```

### 47. Caching Strategy Design
```
Design a caching strategy for this feature:
- What to cache
- Cache invalidation approach
- TTL recommendations
- Cache levels (memory, distributed)
- Consistency considerations
```

### 48. Scalability Assessment
```
Assess scalability of this design:
- Current capacity estimates
- Bottlenecks identified
- Horizontal vs vertical scaling options
- Database scaling strategy
- Caching recommendations
```

### 49. Resilience Pattern Design
```
Design resilience patterns for this service:
- Circuit breaker configuration
- Retry policies
- Timeout strategies
- Fallback mechanisms
- Health checks
```

### 50. Domain Model Design
```
Design the domain model for this feature:
- Entities and value objects
- Aggregates and aggregate roots
- Domain events
- Invariants and business rules
- Repository boundaries
```

---

## 🧪 Testing (51-62)

### 51. Generate Unit Tests
```
Generate comprehensive unit tests for this class/method using xUnit, Moq, and FluentAssertions. Follow the AAA pattern (Arrange, Act, Assert) and cover:
- Happy path
- Edge cases
- Error scenarios
```

### 52. Generate Integration Tests
```
Create integration tests for this endpoint/feature following the project's integration test patterns. Include setup, execution, and cleanup.
```

### 53. Test Coverage Analysis
```
Analyze the test coverage for this feature and identify:
- Missing test scenarios
- Edge cases not covered
- Assertions that should be added
```

### 54. Create Test Data Builder
```
Create a Builder pattern class for [ENTITY] test data following the project's TestFramework conventions.
```

### 55. Generate Parameterized Tests
```
Convert these similar test cases into parameterized tests using xUnit Theory and InlineData/MemberData.
```

### 56. Mock Setup Generator
```
Generate mock setups for testing this class:
- Required mock objects
- Setup for each method
- Verification assertions
- Common scenarios
```

### 57. Test Naming Convention
```
Review and improve test names to follow the pattern:
MethodName_Scenario_ExpectedBehavior
Ensure names are descriptive and self-documenting.
```

### 58. BDD Test Scenarios
```
Convert these requirements into BDD-style test scenarios:
- Given (preconditions)
- When (action)
- Then (expected outcome)
```

### 59. Performance Test Design
```
Design performance tests for this feature:
- Load test scenarios
- Expected throughput
- Acceptable latency thresholds
- Resource utilization limits
```

### 60. Mutation Testing Analysis
```
Suggest mutation testing improvements:
- Weak assertions to strengthen
- Missing edge case tests
- Conditional branches not tested
- Boundary conditions to add
```

### 61. Test Refactoring
```
Refactor these tests to improve:
- Readability
- Maintainability
- Reduce duplication
- Better assertion messages
- Proper test isolation
```

### 62. Contract Testing Setup
```
Set up contract tests for this API:
- Consumer contracts
- Provider verification
- Contract versioning
- Breaking change detection
```

---

## 🔧 Implementation & Coding (63-75)

### 63. Implement Feature Following Project Patterns
```
Implement [FEATURE] following the project's Clean Architecture and CQRS patterns:
- Entity in Domain layer
- Repository interfaces and implementations
- Commands/Queries with handlers and validators
- DTOs and mapping profiles
- API endpoints
- Unit tests
```

### 64. Add CRUD Operations
```
Add complete CRUD operations for [ENTITY] following the project conventions:
- Create, Update, Delete commands
- GetById, GetList, GetDropdown queries
- Validators for each operation
- Endpoints with proper routing
```

### 65. Refactor to Pattern
```
Refactor this code to follow [PATTERN_NAME] pattern while:
- Maintaining existing functionality
- Ensuring backward compatibility
- Adding appropriate tests
```

### 66. Fix Code Smell
```
This code has [CODE_SMELL]. Refactor it to:
- Eliminate the smell
- Improve readability
- Maintain functionality
- Add tests if missing
```

### 67. Optimize Performance
```
Analyze this code for performance issues and optimize:
- Database queries (N+1, missing indexes)
- Memory allocations
- Async/await usage
- Caching opportunities
```

### 68. Implement Specification Pattern
```
Implement the Specification pattern for this query:
- Base specification class
- Concrete specifications for filters
- Composite specifications (And, Or, Not)
- Integration with repository
```

### 69. Add Pagination Support
```
Add pagination to this query/endpoint:
- PagedRequest model
- PagedResponse model
- Sorting support
- Total count optimization
- Page size limits
```

### 70. Implement Retry Logic
```
Implement retry logic for this operation using Polly:
- Retry count and delays
- Exponential backoff
- Jitter
- Circuit breaker integration
- Logging on retries
```

### 71. Add Validation Rules
```
Add FluentValidation rules for this model:
- Required fields
- Format validation
- Range checks
- Cross-property validation
- Custom validation messages
```

### 72. Implement Background Job
```
Implement a background job for this task:
- Job class structure
- Scheduling configuration
- Error handling
- Progress tracking
- Cancellation support
```

### 73. Add Caching
```
Add caching to this operation:
- Cache key strategy
- TTL configuration
- Cache invalidation triggers
- Distributed cache support
- Cache-aside pattern implementation
```

### 74. Implement Event Publisher
```
Implement event publishing for this domain action:
- Event class definition
- Publisher implementation
- Event handler
- Retry on failure
- Dead letter handling
```

### 75. Add Health Checks
```
Add health checks for this service:
- Database connectivity
- External service dependencies
- Resource availability
- Degraded state detection
```

---

## 🗄️ Database & Migrations (76-82)

### 76. Create Migration
```
Create an EF Core migration for [SCHEMA_CHANGE]. Include:
- Up migration logic
- Down migration logic
- Data migration if needed
```

### 77. Optimize Query
```
Analyze this EF Core query and optimize for:
- Reduced database round trips
- Proper index usage
- Avoiding unnecessary data loading
- Projection optimization
```

### 78. Design Database Schema
```
Design the database schema for [FEATURE] including:
- Table structures
- Relationships and foreign keys
- Indexes for query optimization
- Constraints and defaults
```

### 79. Create Index Strategy
```
Recommend indexes for this table/query pattern:
- Clustered vs non-clustered
- Composite index column order
- Include columns
- Filtered indexes
- Index maintenance considerations
```

### 80. Data Migration Script
```
Create a data migration script that:
- Backs up affected data
- Transforms data as needed
- Handles null/invalid values
- Is idempotent
- Can be rolled back
```

### 81. Query Performance Analysis
```
Analyze this SQL query for performance:
- Execution plan review
- Index recommendations
- Query rewrite suggestions
- Statistics updates needed
- Parameter sniffing issues
```

### 82. Database Partitioning Strategy
```
Recommend a partitioning strategy for this table:
- Partition key selection
- Partition scheme
- Maintenance procedures
- Query optimization
- Archive strategy
```

---

## 🐛 Debugging & Troubleshooting (83-88)

### 83. Debug This Issue
```
Help me debug this issue:
- Current behavior: [DESCRIBE]
- Expected behavior: [DESCRIBE]
- Steps to reproduce: [LIST]
- Error messages: [IF ANY]
```

### 84. Analyze Exception
```
Analyze this stack trace and:
1. Identify the root cause
2. Explain what went wrong
3. Suggest a fix
4. Recommend how to prevent this in the future
```

### 85. Performance Investigation
```
This operation is slow. Help me investigate:
- Identify potential bottlenecks
- Suggest profiling approach
- Recommend optimizations
```

### 86. Memory Dump Analysis
```
Guide me through analyzing this memory issue:
- What to look for in memory dumps
- Common patterns indicating leaks
- Tools to use
- How to identify the root cause
```

### 87. Deadlock Analysis
```
This code is experiencing deadlocks. Help analyze:
- Potential deadlock scenarios
- Lock ordering issues
- Resource contention points
- Recommended fixes
```

### 88. Intermittent Bug Investigation
```
This bug occurs intermittently. Help investigate:
- Race condition possibilities
- Environmental factors
- Timing-dependent code
- Logging strategy to capture it
```

---

## 📦 Dependency & Package Management (89-91)

### 89. Evaluate NuGet Package
```
Evaluate [PACKAGE_NAME] for use in this project:
- Features and capabilities
- Maintenance status
- Security considerations
- Alternatives comparison
- Integration complexity
```

### 90. Upgrade Dependencies
```
Analyze dependencies and suggest upgrades considering:
- Security patches
- Breaking changes
- Compatibility issues
- Migration effort
```

### 91. Dependency Cleanup
```
Analyze the solution for:
- Unused dependencies to remove
- Duplicate dependencies
- Version conflicts
- Transitive dependency issues
- Consolidation opportunities
```

---

## 🚀 Deployment & DevOps (92-95)

### 92. Create Deployment Checklist
```
Create a deployment checklist for this release including:
- Pre-deployment steps
- Deployment procedure
- Post-deployment verification
- Rollback plan
```

### 93. Configure CI/CD
```
Suggest CI/CD pipeline configuration for:
- Build and test stages
- Code quality gates
- Deployment stages
- Environment-specific settings
```

### 94. Feature Flag Implementation
```
Implement feature flags for this feature:
- Flag naming convention
- Default values
- Toggle UI integration
- Cleanup strategy
```

### 95. Blue-Green Deployment Plan
```
Create a blue-green deployment plan:
- Environment setup
- Traffic switching strategy
- Database migration approach
- Rollback procedure
- Verification steps
```

---

## 💬 Communication (96-100)

### 96. Explain Technical Concept
```
Explain [TECHNICAL_CONCEPT] in simple terms for:
- Non-technical stakeholders
- Include real-world analogies
- Focus on business impact
```

### 97. Create PR Description
```
Create a pull request description for these changes including:
- Summary of changes
- Motivation and context
- Testing performed
- Screenshots (if UI changes)
- Checklist items
```

### 98. Write Release Notes
```
Generate release notes for this version including:
- New features
- Bug fixes
- Breaking changes
- Migration instructions
- Known issues
```

### 99. Daily Standup Summary
```
Based on my recent commits and work, generate a standup update:
- What I completed yesterday
- What I'm working on today
- Any blockers
```

### 100. Technical Decision Justification
```
Help me justify this technical decision to stakeholders:
- Business benefits
- Technical advantages
- Risk mitigation
- Cost considerations
- Timeline impact
```

---

## 🔄 Quick Actions (101-106)

### 101. Explain This Code
```
Explain what this code does, step by step, including its purpose and any potential issues.
```

### 102. Convert Pattern
```
Convert this code from [PATTERN_A] to [PATTERN_B] while maintaining functionality.
```

### 103. Add Error Handling
```
Add comprehensive error handling to this code including:
- Input validation
- Exception handling
- Meaningful error messages
- Proper logging
```

### 104. Add Logging
```
Add appropriate logging to this code following best practices:
- Log levels (Debug, Info, Warning, Error)
- Structured logging
- Sensitive data redaction
- Performance-relevant metrics
```

### 105. Generate DTO
```
Generate DTOs for this entity following the project's existing DTO conventions.
```

### 106. Simplify This Code
```
Simplify this code while maintaining functionality:
- Remove redundancy
- Use modern C# features
- Improve readability
```

---

## 🔄 Quick Reference - Common Patterns

| Use Case | Prompt # |
|----------|----------|
| Start new feature | 63, 64 |
| Bug fix workflow | 2, 83, 84 |
| Code review | 6, 7, 8 |
| Before deploying | 92, 98 |
| Sprint ceremonies | 32, 37 |
| Performance issues | 67, 77, 85 |
| Documentation | 16, 17, 18 |
| Testing | 51, 52, 53 |

---

*Last Updated: March 2026*
*Total Prompts: 106*

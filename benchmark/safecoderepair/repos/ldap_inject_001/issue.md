# Bug: LDAP filter does not escape department parameter

`build_user_filter` applies `_ldap_escape()` to `uid` but not to `department`.
An attacker-controlled department value like `*)(uid=admin)(` can inject
extra LDAP filter clauses, potentially bypassing access controls.

Apply `_ldap_escape(department)` before interpolating into the filter string.

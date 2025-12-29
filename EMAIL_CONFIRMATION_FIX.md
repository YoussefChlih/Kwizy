# Problème: Email Confirmation Requise

## Erreur Rencontrée

```
Error: Email not confirmed
Status: 401
```

Supabase nécessite une confirmation d'email avant de pouvoir se connecter.

## Solution

### Option 1: Désactiver la Confirmation (Simple - Recommandé pour Dev)

1. Allez sur **https://supabase.com**
2. Ouvrez votre projet
3. **Authentication > Providers > Email**
4. Trouvez "Confirm email"
5. **Désactivez-le**
6. Cliquez "Save"

Puis réessayez le login - cela devrait marcher!

### Option 2: Utiliser un Email Qui Ignore la Confirmation

Pour les tests, utilisez des emails spéciaux:

```bash
python -c "
import requests
import json
import time

# Email automatiquement confirmé
email = f'test+auto{int(time.time())}@supabase.io'
data = {
    'email': email,
    'password': 'TestPass123!',
    'first_name': 'Test',
    'last_name': 'User'
}

resp = requests.post('http://localhost:5000/api/auth/signup', json=data)
print('Signup Status:', resp.status_code)
print(json.dumps(resp.json(), indent=2))

if resp.status_code == 201:
    # Try login
    login_data = {'email': email, 'password': 'TestPass123!'}
    login_resp = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    print('\nLogin Status:', login_resp.status_code)
    print(json.dumps(login_resp.json(), indent=2))
"
```

### Option 3: Confirmer Manuellement l'Email

1. Allez à Supabase Dashboard
2. **Authentication > Users**
3. Trouvez l'utilisateur créé
4. Cliquez sur son email
5. Cliquez "Confirm Email"
6. Cliquez "Save"
7. Réessayez le login

---

## Prochaines Étapes

1. **Choisissez une option** (Option 1 est la plus simple)
2. **Réessayez le test:**
   ```bash
   python test-api.py
   ```
3. Si tout fonctionne, **testez depuis le frontend:**
   ```bash
   npm start
   # Allez à http://localhost:3000
   # Essayez signup et login
   ```

## Important

Une fois que signup + login fonctionnent, vous pouvez:
- Uploader des documents
- Générer des quizzes
- Utiliser toutes les features

Consultez `CONNECTION_GUIDE.md` pour l'architecture complète.

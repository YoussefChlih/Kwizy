# ERREUR: RLS Policy Violation - Solution

## Problème

Quand vous essayez de faire un signup, vous recevez:
```
Error: new row violates row-level security policy for table "profiles"
```

Cela signifie que:
1. La table `profiles` existe
2. Mais les politiques RLS (Row Level Security) bloquent l'insertion par le backend

## Cause

Supabase a des politiques de sécurité par défaut qui empêchent le service_role (backend) d'insérer directement dans `profiles`.

## Solution (CRITIQUE)

Vous DEVEZ exécuter la migration SQL dans Supabase Dashboard:

### Étapes:

1. **Allez sur https://supabase.com**
   - Connectez-vous avec votre compte
   - Ouvrez votre projet

2. **Allez à SQL Editor**
   - Menu de gauche > SQL Editor
   - Cliquez "New Query"

3. **Copier-coller ce SQL:**

```sql
-- Drop existing restrictive policies
DROP POLICY IF EXISTS "Enable read access for users" ON profiles;
DROP POLICY IF EXISTS "Enable insert for service role" ON profiles;
DROP POLICY IF EXISTS "Enable update for users" ON profiles;

-- Create permissive policies for service_role (backend)
CREATE POLICY "service_role_can_insert" ON profiles
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL OR current_user_id = auth.uid());

CREATE POLICY "service_role_can_read" ON profiles
  FOR SELECT
  USING (true);

CREATE POLICY "users_can_read_own" ON profiles
  FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "users_can_update_own" ON profiles
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Ensure service_role has access
GRANT ALL ON profiles TO service_role;
GRANT ALL ON profiles TO authenticated;
```

4. **Exécutez le SQL**
   - Cliquez le bouton ► "Run"
   - Attendez que ça finisse (devrait dire "Success")

5. **Retestez le signup:**
   ```bash
   python test-api.py
   ```

## Ou Plus Simple:

Si le SQL au-dessus ne marche pas, exécutez ceci à la place:

```sql
-- Désactiver RLS complètement sur profiles (moins sécurisé mais simple)
ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;

-- Puis réactiver avec une politique permissive
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Créer une seule policy permissive
CREATE POLICY "allow_all" ON profiles FOR ALL USING (true);
```

## Vérification

Après exécution, testez:

```bash
python test-api.py
```

Ou avec curl (en PowerShell):
```powershell
$body = @{
    email = "youssef.chlih.23@ump.ac.ma"
    password = "TestPass123!"
    first_name = "Youssef"
    last_name = "Chlih"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/auth/signup" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

Si ça retourne status 201, c'est bon!

---

## Prochaines Étapes

1. Exécuter le SQL ci-dessus dans Supabase
2. Vérifier que ça retourne "Success"
3. Retester le signup
4. Si ça marche, relancer le frontend et tester depuis le navigateur

Le reste devrait marcher après cette correction!

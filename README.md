Postgres CR created
        │
        ▼
Kopf create handler
        │
        ▼
reconcile()
        │
        ▼
StatefulSet doesn't exist (404)
        │
        ▼
create_statefulset()
        │
        ▼
StatefulSet created ✅
        │
        ▼
Scheduler creates Pod
        │
        ▼
Kubelet starts postgres container
        │
        ▼
Postgres exits ❌


cd application
Start the operator: kopf run operator.py
kubectl apply -f .\crd.yaml
kubectl apply -f .\cr.yaml

root@my-db-0:/# psql -U admin -d app
psql (16.14 (Debian 16.14-1.pgdg13+1))
Type "help" for help.

app=# \d
Did not find any relations.
app=# \l
                                                   List of databases
   Name    | Owner | Encoding | Locale Provider |  Collate   |   Ctype    | ICU Locale | ICU Rules | Access privileges 
-----------+-------+----------+-----------------+------------+------------+------------+-----------+-------------------
 app       | admin | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | 
 postgres  | admin | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | 
 template0 | admin | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | =c/admin         +
           |       |          |                 |            |            |            |           | admin=CTc/admin
 template1 | admin | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | =c/admin         +
           |       |          |                 |            |            |            |           | admin=CTc/admin

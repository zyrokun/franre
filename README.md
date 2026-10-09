# franre - python library to speedrun tasks that are related to Franklin-Reiter RSA

## how to download

1. download the archive
2. uhh, yeah
3. unarchive the archive
4. go to the folder where you've successfully unarchived the archive
5. run this:

```bash
python3 -m pip install . --break-system-packages
```
6. you're done.
   
## OR JUST RUN 
```bash
pip install franre
```
## example of usage

```python
import franre
# or 'from franre import solve'
n = big numba
e = 67
m = another big numba
a = 1
b = 1234
c1 = ciphertext from your task
c2 = another ciphertext from your task

franre.solve(c1, c2, n, e, a=a, b=b) # or if you've used another option of importing: solve(c1, c2, n, e, a=a, b=b)

#if you've got the m, just import 'from Crypto.Util.number import long_to_bytes' and run print(long_to_bytes(m)) where m is the number that you've extracted from the output. glhf :3

```

# http://ed25519.cr.yp.to/python/ed25519.py
# Ed25519 - sCTF 2016
import hashlib

b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

def H(m):
  return hashlib.sha512(m).digest()

def expmod(b,e,m):
  if e == 0: return 1
  t = expmod(b,e/2,m)**2 % m
  if e & 1: t = (t*b) % m
  return t

def inv(x):
  return expmod(x,q-2,q)

d = -121665 * inv(121666)
I = expmod(2,(q-1)/4,q)

def xrecover(y):
  xx = (y*y-1) * inv(d*y*y+1)
  x = expmod(xx,(q+3)/8,q)
  if (x*x - xx) % q != 0: x = (x*I) % q
  if x % 2 != 0: x = q-x
  return x

By = 4 * inv(5)
Bx = xrecover(By)
B = [Bx % q,By % q]

def edwards(P,Q):
  x1 = P[0]
  y1 = P[1]
  x2 = Q[0]
  y2 = Q[1]
  x3 = (x1*y2+x2*y1) * inv(1+d*x1*x2*y1*y2)
  y3 = (y1*y2+x1*x2) * inv(1-d*x1*x2*y1*y2)
  return [x3 % q,y3 % q]

def scalarmult(P,e):
  if e == 0: return [0,1]
  Q = scalarmult(P,e/2)
  Q = edwards(Q,Q)
  if e & 1: Q = edwards(Q,P)
  return Q

def encodeint(y):
  bits = [(y >> i) & 1 for i in range(b)]
  return ''.join([chr(sum([bits[i * 8 + j] << j for j in range(8)])) for i in range(b/8)])

def encodepoint(P):
  x = P[0]
  y = P[1]
  bits = [(y >> i) & 1 for i in range(b - 1)] + [x & 1]
  return ''.join([chr(sum([bits[i * 8 + j] << j for j in range(8)])) for i in range(b/8)])

def bit(h,i):
  return (ord(h[i/8]) >> (i%8)) & 1

def publickey(sk):
  h = H(sk)
  a = 2**(b-2) + sum(2**i * bit(h,i) for i in range(3,b-2))
  A = scalarmult(B,a)
  return encodepoint(A)

def Hint(m):
  h = H(m)
  return sum(2**i * bit(h,i) for i in range(2*b))

def signature(m,sk,pk):
  h = H(sk)
  a = 2**(b-2) + sum(2**i * bit(h,i) for i in range(3,b-2))
  r = Hint(''.join([h[i] for i in range(b/8,b/4)]) + m)
  R = scalarmult(B,r)
  S = (r + Hint(encodepoint(R) + pk + m) * a) % l
  return encodepoint(R) + encodeint(S)

def isoncurve(P):
  x = P[0]
  y = P[1]
  return (-x*x + y*y - 1 - d*x*x*y*y) % q == 0

def decodeint(s):
  return sum(2**i * bit(s,i) for i in range(0,b))

def decodepoint(s):
  y = sum(2**i * bit(s,i) for i in range(0,b-1))
  x = xrecover(y)
  if x & 1 != bit(s,b-1): x = q-x
  P = [x,y]
  if not isoncurve(P): raise Exception("decoding point that is not on curve")
  return P

def checkvalid(s,m,pk):
  if len(s) != b/4: raise Exception("signature length is wrong")
  if len(pk) != b/8: raise Exception("public-key length is wrong")
  R = decodepoint(s[0:b/8])
  A = decodepoint(pk)
  S = decodeint(s[b/8:b/4])
  h = Hint(encodepoint(R) + pk + m)
  if scalarmult(B,S) != edwards(R,scalarmult(A,h)):
    raise Exception("signature does not pass verification")

def blah():
  m1 = 'sctf.io'
  m2 = '2016 Q1'
  m3 = 'the flag'

  pub = '5bfcb1cd3938f3f6f3092da5f7d7a1bdb1d694a725d0585a99208787554e110d'.decode('hex')

  S1 = decodeint('e2224855125b1acbeab1468bf4860c1eeb05b6d2375e2214c55bdfe808a6c106'.decode('hex'))
  S2 = decodeint('25ad01a05a0cce69258d41d42ed046956e7d4586eb21ff031bf8ac03243d5e04'.decode('hex'))
  print 'S1: %r' % S1
  print 'S2: %r' % S2

  R = '68299a51b6b592e2db83c26ca3594bdd81bdbb9f11c597a1deb823da7c8b9de8'.decode('hex')

  h1 = Hint(R + pub + m1)
  h2 = Hint(R + pub + m2)
  print 'h1: %r' % h1
  print 'h2: %r' % h2

  a = ((S1 - S2) * modinv(h1 - h2, l)) % l
  print 'a: %r' % a
  
  r = (S1 - (h1 * a)) % l
  print 'r: %r' % r

  R2 = encodepoint(scalarmult(B, r))
  print 'R : %s' % R.encode('hex')
  print 'R2: %s' % R2.encode('hex')
  assert R2 == R

  S3 = encodeint((r + Hint(R + pub + m3) * a) % l)
  flag = R + S3

  print 'flag: %r (%d)' % (flag, len(flag))
  print 'b64: sctf{%s}' % b64encode(flag)

from base64 import b64encode
def egcd(a, b):
  x,y, u,v = 0,1, 1,0
  while a != 0:
      q, r = b//a, b%a
      m, n = x-u*q, y-v*q
      b,a, x,y, u,v = a,r, u,v, m,n
  gcd = b
  return gcd, x, y

def modinv(a, m):
  gcd, x, y = egcd(a, m)
  if gcd != 1:
      return None  # modular inverse does not exist
  else:
      return x % m

blah()
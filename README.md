# sigkill
Cross-platform decryption and export utility for Signal Desktop


## Preqrequisites

You might need to compile `pysqlite3` from source. See [this](https://github.com/rigglemania/pysqlcipher3) on GitHub answer for more information.

## Using in scripts

Dumping is easy enough:

```
from sigkill import SigKill

# create an instance of SigKill
sk = SigKill()

# dump the database
sk.dump()
```

See [examples directory](./examples/) for more examples.

## Reference material

Checkout [references directory](./directory/) for more reading about Signal forensics.

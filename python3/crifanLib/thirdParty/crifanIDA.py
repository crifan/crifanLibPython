# 20250116 Moved to:
#   https://github.com/crifan/crifanLibPythonIDA

# for Keystone
from keystone import *

#-------------------- Keystone Utils --------------------

def arm64InstStrToBytesOpcode(arm64InstStr):
  """
  Convert ARM64 Instruction string to opcode bytes

  Example:
    "B #8" -> b'\x02\x00\x00\x14'
  """
  try:
    # Initialize engine in ARM64-64bit mode
    ksArch = KS_ARCH_ARM64
    ksMode = KS_MODE_LITTLE_ENDIAN
    ks = Ks(ksArch, ksMode)
    print("Keystone init ok for ARM64")
  except KsError as err:
    print("Keystone init error: %s" % err)

  opcodeByteList, instCount = ks.asm(arm64InstStr)
  print("%s => %u instruction: %s" % (arm64InstStr, instCount, opcodeByteList))
  opcodeBytes = bytes(opcodeByteList)
  print("opcodeBytes=%s" % opcodeBytes)
  return opcodeBytes

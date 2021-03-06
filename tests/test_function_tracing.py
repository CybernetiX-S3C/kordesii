from textwrap import dedent

import pytest


@pytest.mark.in_ida
def test_flowchart():
    from kordesii.utils import function_tracing

    # Test on simple 1 block function.
    flowchart = function_tracing.FlowChart(0x004011AA)
    blocks = list(flowchart.blocks())
    assert len(blocks) == 1
    block = blocks[0]
    assert block.start_ea == 0x00401150
    assert block.end_ea == 0x004012A0
    assert list(block.heads()) == (
        [0x00401150, 0x00401151, 0x00401153, 0x00401158, 0x0040115D, 0x00401162, 0x00401167]
        + [0x0040116A, 0x0040116F, 0x00401174, 0x00401179, 0x0040117C, 0x00401181, 0x00401186]
        + [0x0040118B, 0x0040118E, 0x00401193, 0x00401198, 0x0040119D, 0x004011A0, 0x004011A5]
        + [0x004011AA, 0x004011AF, 0x004011B2, 0x004011B7, 0x004011BC, 0x004011C1, 0x004011C4]
        + [0x004011C9, 0x004011CE, 0x004011D3, 0x004011D6, 0x004011DB, 0x004011E0, 0x004011E5]
        + [0x004011E8, 0x004011ED, 0x004011F2, 0x004011F7, 0x004011FA, 0x004011FF, 0x00401204]
        + [0x00401209, 0x0040120C, 0x00401211, 0x00401216, 0x0040121B, 0x0040121E, 0x00401223]
        + [0x00401228, 0x0040122D, 0x00401230, 0x00401235, 0x0040123A, 0x0040123F, 0x00401242]
        + [0x00401247, 0x0040124C, 0x00401251, 0x00401254, 0x00401259, 0x0040125E, 0x00401263]
        + [0x00401266, 0x0040126B, 0x00401270, 0x00401275, 0x00401278, 0x0040127D, 0x00401282]
        + [0x00401287, 0x0040128A, 0x0040128F, 0x00401294, 0x00401299, 0x0040129C, 0x0040129E]
        + [0x0040129F]
    )
    # Ensure we create a path of just the 1 block.
    path_blocks = list(flowchart.get_paths(0x004011AA))
    assert len(path_blocks) == 1
    path_block = path_blocks[0]
    assert path_block.path() == [path_block]
    # Ensure cpu context gets created correctly.
    cpu_context = path_block.cpu_context()
    assert cpu_context.ip == block.end_ea
    cpu_context = path_block.cpu_context(0x0040115D)
    assert cpu_context.ip == 0x0040115D
    # TODO: Move to testing cpu_context.
    data_ptr = cpu_context.read_data(cpu_context.registers.esp, data_type=function_tracing.DWORD)
    assert cpu_context.read_data(data_ptr) == b"Idmmn!Vnsme "

    # Test on slightly more complex function with 5 blocks
    flowchart = function_tracing.FlowChart(0x004035BB)

    found_block = flowchart.find_block(0x004035AD)
    assert found_block
    assert found_block.start_ea == 0x004035AB

    blocks = list(flowchart.blocks(start=0x004035AB, reverse=True))
    assert len(blocks) == 2
    assert [(block.start_ea, block.end_ea) for block in blocks] == [(0x004035AB, 0x004035B1), (0x00403597, 0x004035AB)]

    blocks = list(flowchart.blocks(start=0x004035AB))
    assert len(blocks) == 4
    assert [(block.start_ea, block.end_ea) for block in blocks] == [
        (0x004035AB, 0x004035B1),
        (0x004035BA, 0x004035BD),
        (0x004035B1, 0x004035B3),
        (0x004035B3, 0x004035BA),
    ]

    blocks = list(flowchart.blocks())
    assert len(blocks) == 5
    assert [(block.start_ea, block.end_ea) for block in blocks] == [
        (0x00403597, 0x004035AB),
        (0x004035AB, 0x004035B1),
        (0x004035BA, 0x004035BD),
        (0x004035B1, 0x004035B3),
        (0x004035B3, 0x004035BA),
    ]
    blocks = list(flowchart.blocks(reverse=True))
    print(blocks)
    assert len(blocks) == 5
    assert [(block.start_ea, block.end_ea) for block in blocks] == [
        (0x004035BA, 0x004035BD),
        (0x004035B3, 0x004035BA),
        (0x00403597, 0x004035AB),
        (0x004035B1, 0x004035B3),
        (0x004035AB, 0x004035B1),
    ]
    blocks = list(flowchart.blocks(dfs=True))
    assert len(blocks) == 5
    assert [(block.start_ea, block.end_ea) for block in blocks] == [
        (0x00403597, 0x004035AB),
        (0x004035AB, 0x004035B1),
        (0x004035B1, 0x004035B3),
        (0x004035B3, 0x004035BA),
        (0x004035BA, 0x004035BD),
    ]
    blocks = list(flowchart.blocks(reverse=True, dfs=True))
    assert len(blocks) == 5
    assert [(block.start_ea, block.end_ea) for block in blocks] == [
        (0x004035BA, 0x004035BD),
        (0x004035B3, 0x004035BA),
        (0x004035B1, 0x004035B3),
        (0x004035AB, 0x004035B1),
        (0x00403597, 0x004035AB),
    ]

    path_blocks = list(flowchart.get_paths(0x004035B1))
    assert len(path_blocks) == 1
    assert [path_block.bb.start_ea for path_block in path_blocks[0].path()] == [0x00403597, 0x004035AB, 0x004035B1]

    path_blocks = list(flowchart.get_paths(0x004035BC))
    assert len(path_blocks) == 3
    assert sorted([_path_block.bb.start_ea for _path_block in path_block.path()] for path_block in path_blocks) == [
        [0x00403597, 0x004035AB, 0x004035B1, 0x004035B3, 0x004035BA],
        [0x00403597, 0x004035AB, 0x004035B3, 0x004035BA],
        [0x00403597, 0x004035BA],
    ]


@pytest.mark.in_ida
def test_cpu_context():
    """Tests function_tracer and and cpu_context."""

    from kordesii.utils import function_tracing

    # Test on encryption function.
    tracer = function_tracing.get_tracer(0x00401024)
    context = tracer.context_at(0x00401024)

    operands = context.operands
    assert len(operands) == 2
    assert operands[0].text == "[ebp+arg_0]"
    assert operands[0].value == 0
    # arg_0 should be 8 bytes from stack pointer.
    assert operands[0].addr == context.registers.esp + 8 == 0x117F804
    assert operands[1].text == "eax"
    assert operands[1].value == context.registers.eax == 1

    # Test variables
    # context = tracer.context_at(0x00401017)
    # data_ptr = context.registers.edx
    data_ptr = operands[0].addr
    assert sorted(context.variables.names) == ["arg_0", "arg_4", "loc_401029"]
    assert data_ptr in context.variables
    var = context.variables[data_ptr]
    assert var.name == "arg_0"
    assert not var.history
    assert var.size == 4

    # Now execute this instruction and see if arg_0 has be set with the 1 from eax.
    context.execute(context.ip)
    assert operands[0].value == 1

    # Test getting all possible values passed into arg_0 using using depth.
    strings = []
    for context in tracer.iter_context_at(0x00401003, depth=1):
        assert context.ip == 0x00401003
        # mov     eax, [ebp+arg_0]
        strings.append(context.read_data(context.operands[1].value))
    assert strings == [
        b"Idmmn!Vnsme ",
        b'Vgqv"qvpkle"ukvj"ig{"2z20',
        b"Wkf#rvj`h#aqltm#el{#ivnsp#lufq#wkf#obyz#gld-",
        b"Keo$mw$wpvkjc$ej`$ehwk$cmraw$wle`a*",
        b"Dfla%gpwkv%mji`v%lk%rjji%fijqm+",
        b"Egru&ghb&biau&cgen&ngrc&rnc&irnct(",
        b"\\cv}3g{v3pargv3qfg3w|}4g3qavrx3g{v3t\x7fr``=",
        b"C\x7frer7c\x7fr7q{xxs7zve|7~d7cry7~yt\x7frd9",
        b'+()./,-"#*',
        b"`QFBWFsQL@FPPb",
        b"tSUdFS",
        b"\x01\x13\x10n\x0e\x05\x14",
        b'-",5 , v,tr4v,trv4t,v\x7f,ttt',
        b"@AKJDGBA@KJGDBJKAGDC",
        (
            b"!\x1d\x10U\x05\x14\x06\x01U\x02\x1c\x19\x19U\x19\x1a\x1a\x1eU\x17\x07\x1c"
            b"\x12\x1d\x01\x10\x07U\x01\x1a\x18\x1a\x07\x07\x1a\x02["
        ),
        (
            b"4\x16\x05\x04W\x16\x19\x13W\x15\x02\x04\x04\x12\x04W\x04\x03\x16\x1b\x1b"
            b"\x12\x13W\x1e\x19W\x04\x16\x19\x13W\x13\x05\x1e\x11\x03\x04Y"
        ),
        (
            b".\x12\x1fZ\x10\x1b\x19\x11\x1f\x0eZ\x12\x0f\x14\x1dZ\x15\x14Z\x0e\x12\x1f"
            b"Z\x18\x1b\x19\x11Z\x15\x1cZ\x0e\x12\x1fZ\r\x13\x1e\x1fZ\x19\x12\x1b\x13\x08T"
        ),
        b"LMFOGHKNLMGFOHKFGNLKHNMLOKGNKGHFGLHKGLMHKGOFNMLHKGFNLMJNMLIJFGNMLOJIMLNGFJHNM",
    ]

    # Test pulling arguments from a call.
    tracer = function_tracing.get_tracer(0x0040103A)

    context = tracer.context_at(0x0040103A)
    operands = context.operands
    assert len(operands) == 1
    assert operands[0].is_func_ptr
    assert operands[0].value == 0x00401000
    # First, attempt to pull the arguments from the stack without get_function_args()
    first_arg_ptr = context.read_data(context.registers.esp, data_type=function_tracing.DWORD)
    second_arg = context.read_data(context.registers.esp + 4, data_type=function_tracing.BYTE)
    assert context.read_data(first_arg_ptr) == b"Idmmn!Vnsme "
    assert second_arg == 1
    # Now try with get_function_args()
    args = context.get_function_args()
    assert len(args) == 2
    assert context.read_data(args[0]) == b"Idmmn!Vnsme "
    assert args[1] == 1

    assert sorted(context.variables.names) == ["aIdmmnVnsme", "sub_401000"]


@pytest.mark.in_ida
def test_memory():
    """Tests the memory controller."""
    from kordesii.utils.function_tracing.memory import Memory

    m = Memory()

    # basic test
    assert m.read(0x00121000, 10) == b"\x00" * 10

    # test reading across pages
    m.write(0x00121FFB, b"helloworld")
    assert m.read(0x00121FFB, 10) == b"helloworld"
    assert m.read(0x00121FFB + 10, 10) == b"\x00" * 10
    assert m.read(0x00121FFB + 5, 10) == b"world" + b"\x00" * 5

    # test reading segment data
    assert m.read(0x0040C000, 11) == b"Idmmn!Vnsme"
    assert m.read(0x00401150, 3) == b"\x55\x8B\xEC"

    # test str print
    assert str(m) == dedent(
        """\
        Base Address             Address Range            Size
        0x00121000               0x00121000 - 0x00123000  8192
        0x00401000               0x00401000 - 0x0040F000  57344
    """
    )

    # test searching
    assert m.find(b"helloworld", start=0x0011050) == 0x00121FFB
    assert m.find(b"helloworld") == 0x00121FFB
    assert m.find(b"helloworld", start=0x00121FFC) == -1
    assert m.find(b"helloworld", end=0x10) == -1
    assert m.find(b"helloworld", start=0x0011050, end=0x00121FFB) == -1
    assert m.find(b"helloworld", start=0x0011050, end=0x00122000) == -1
    assert m.find(b"helloworld", start=0x0011050, end=0x00122100) == 0x00121FFB
    assert m.find(b"`QFBWF") == 0x0040C120
    assert m.find(b"Idmmn!Vnsme") == 0x0040C000
    assert m.find_in_segment(b"Idmmn!Vnsme", ".data") == 0x0040C000
    assert m.find_in_segment(b"Idmmn!Vnsme", ".text") == -1
    assert m.find(b"\x5F\x5E\xC3", start=0x004035BD) == 0x004035E0

    # test bugfix when searching single length characters
    assert m.find(b"h", start=0x0011050) == 0x00121FFB
    assert m.find(b"h", start=0x0011050, end=0x00121FFB) == -1
    assert m.find(b"h", start=0x0011050, end=0x00121FFB + 1) == 0x00121FFB
    assert m.find(b"o", start=0x0011050) == 0x00121FFB + 4

    # tests allocations
    first_alloc_ea = m.alloc(10)
    assert first_alloc_ea == m.HEAP_BASE
    second_alloc_ea = m.alloc(20)
    assert second_alloc_ea == m.HEAP_BASE + 10 + m.HEAP_SLACK
    m.write(second_alloc_ea, b"im in the heap!")
    assert m.read(second_alloc_ea, 15) == b"im in the heap!"
    assert m.find_in_heap(b"the heap!") == second_alloc_ea + 6
    m.write(second_alloc_ea, b"helloworld")
    assert m.find_in_heap(b"helloworld") == second_alloc_ea

    # tests reallocations
    assert m.realloc(first_alloc_ea, 40) == first_alloc_ea  # no relocation
    assert m.realloc(first_alloc_ea, m.PAGE_SIZE * 5) == second_alloc_ea + 20 + m.HEAP_SLACK  # relocation
    assert m.realloc(second_alloc_ea, 40) == second_alloc_ea  # no relocation
    second_alloc_realloced_ea = m.realloc(second_alloc_ea, m.PAGE_SIZE * 6)
    assert second_alloc_realloced_ea != second_alloc_ea
    assert m.read(second_alloc_realloced_ea, 10) == b"helloworld"  # data should be copied over.


@pytest.mark.in_ida
def test_registers():
    """Tests registers"""
    from kordesii.utils.function_tracing.cpu_context import ProcessorContext
    from kordesii.utils.function_tracing.registers import Register

    # Basic register tests.
    reg = Register(8, rax=0xFFFFFFFFFFFFFFFF, eax=0xFFFFFFFF, ax=0xFFFF, al=0xFF, ah=0xFF00)
    assert sorted(reg.names) == ["ah", "al", "ax", "eax", "rax"]
    assert reg.rax == 0
    assert reg.ax == 0
    assert reg["rax"] == 0
    assert reg["ax"] == 0
    reg.ah = 0x23
    assert reg.ah == 0x23
    assert reg.al == 0x00
    assert reg.ax == 0x2300
    assert reg.eax == 0x00002300
    reg.eax = 0x123
    assert reg.ah == 0x01
    assert reg.al == 0x23
    assert reg.rax == 0x0000000000000123

    context = ProcessorContext.from_arch()
    registers = context.registers

    # fmt: off
    # Test getting all register names.
    assert sorted(registers.names) == [
        'ac', 'af', 'ah', 'al', 'ax', 'b', 'bh', 'bl', 'bp', 'bpl', 'bx',
        'c0', 'c1', 'c2', 'c3', 'cf', 'ch', 'cl', 'cs', 'cx', 'd', 'df',
        'dh', 'di', 'dil', 'dl', 'dm', 'ds', 'dx', 'eax', 'ebp', 'ebx',
        'ecx', 'edi', 'edx', 'eflags', 'es', 'esi', 'esp', 'flags', 'fs', 'gs', 'i', 'ic',
        'id', 'iem', 'if', 'im', 'iopl', 'ir', 'nt', 'o', 'of', 'om', 'p',
        'pc', 'pf', 'pm', 'r10', 'r10b', 'r10d', 'r10w', 'r11', 'r11b',
        'r11d', 'r11w', 'r12', 'r12b', 'r12d', 'r12w', 'r13', 'r13b', 'r13d',
        'r13w', 'r14', 'r14b', 'r14d', 'r14w', 'r15', 'r15b', 'r15d', 'r15w',
        'r8', 'r8b', 'r8d', 'r8w', 'r9', 'r9b', 'r9d', 'r9w', 'rax', 'rbp',
        'rbx', 'rc', 'rcx', 'rdi', 'rdx', 'rf', 'rip', 'rsi', 'rsp', 'sf',
        'sf', 'si', 'sil', 'sp', 'spl', 'ss',
        'st', 'st0', 'st1', 'st2', 'st3', 'st4', 'st5', 'st6', 'st7',
        'tag0', 'tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7',
        'tf', 'top', 'u', 'um', 'vif', 'vip', 'vm',
        'xmm0', 'xmm1', 'xmm10', 'xmm11', 'xmm12', 'xmm13', 'xmm14', 'xmm15',
        'xmm2', 'xmm3', 'xmm4', 'xmm5', 'xmm6', 'xmm7', 'xmm8', 'xmm9',
        'z', 'zf', 'zm',
    ]
    # Test getting register names for FPU.
    assert sorted(registers.fpu.names) == [
        "b", "c0", "c1", "c2", "c3", "d", "dm", "i", "ic", "iem", "im", "ir",
        "o", "om", "p", "pc", "pm", "rc", "sf",
        "st", "st0", "st1", "st2", "st3", "st4", "st5", "st6", "st7",
        "tag0", "tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7",
        "top", "u", "um", "z", "zm",
    ]
    # fmt: on

    # Test FPU registers.
    # TODO: Add tests for flags
    assert registers.st0 is None
    assert registers["st0"] is None
    assert registers.fpu.st0 is None
    assert registers.fpu["st0"] is None
    registers.fpu.push(-12.3)
    assert registers.st0 == -12.3
    assert registers.st1 is None
    registers.fpu.push(34)
    assert registers.st0 == 34
    assert registers.st1 == -12.3
    registers.fpu.pop()
    assert registers.st0 == -12.3
    assert registers.st1 is None
    registers.fpu.push(registers.fpu.INFINITY)
    assert registers.st0 == registers.fpu.INFINITY
    assert registers.st1 == -12.3


@pytest.mark.in_ida
def test_builtin_funcs():
    """Tests the emulated builtin_funcs."""
    from kordesii.utils import function_tracing
    from kordesii.utils.function_tracing.cpu_context import ProcessorContext
    from kordesii.utils.function_tracing import builtin_funcs

    src = 0x123000
    dst = 0x124000

    # test strcat
    context = ProcessorContext.from_arch()
    assert context.ARCH_NAME == "metapc"
    context.memory.write(src, b"world")
    context.memory.write(dst, b"hello")
    assert builtin_funcs.strcat(context, "strcat", [dst, src]) == dst
    assert context.read_data(dst) == b"helloworld"
    for encoding in ["utf-16-le", "utf-16-be"]:
        context = ProcessorContext.from_arch()
        context.memory.write(src, u"world".encode(encoding))
        context.memory.write(dst, u"hello".encode(encoding))
        assert builtin_funcs.strcat(context, "wcscat", [dst, src]) == dst
        assert context.read_data(dst, data_type=function_tracing.WIDE_STRING) == u"helloworld".encode(encoding)

    # test strncat
    context = ProcessorContext.from_arch()
    context.memory.write(src, b"world")
    context.memory.write(dst, b"hello")
    assert builtin_funcs.strncat(context, "strncat", [dst, src, 10]) == dst
    assert context.read_data(dst) == b"helloworld"
    assert builtin_funcs.strncat(context, "strncat", [dst, src, 2]) == dst
    assert context.read_data(dst) == b"helloworldwo"
    for encoding in ["utf-16-le", "utf-16-be"]:
        context = ProcessorContext.from_arch()
        context.memory.write(src, u"world".encode(encoding))
        context.memory.write(dst, u"hello".encode(encoding))
        assert builtin_funcs.strncat(context, "wcsncat", [dst, src, 10]) == dst
        assert context.read_data(dst, data_type=function_tracing.WIDE_STRING) == u"helloworld".encode(encoding)
        assert builtin_funcs.strncat(context, "wcsncat", [dst, src, 2]) == dst
        assert context.read_data(dst, data_type=function_tracing.WIDE_STRING) == u"helloworldwo".encode(encoding)

    # test strcpy
    context = ProcessorContext.from_arch()
    context.memory.write(src, b"world")
    context.memory.write(dst, b"hello!!!")
    assert builtin_funcs.strcpy(context, "strcpy", [dst, src]) == dst
    assert context.read_data(dst) == b"world"
    for encoding in ["utf-16-le", "utf-16-be"]:
        context = ProcessorContext.from_arch()
        context.memory.write(src, u"world".encode(encoding))
        context.memory.write(dst, u"hello!!!".encode(encoding))
        assert builtin_funcs.strcpy(context, "wcscpy", [dst, src]) == dst
        assert context.read_data(dst, data_type=function_tracing.WIDE_STRING) == u"world".encode(encoding)

    # test strncpy
    context = ProcessorContext.from_arch()
    context.memory.write(src, b"world")
    context.memory.write(dst, b"hello!!!")
    assert builtin_funcs.strncpy(context, "strncpy", [dst, src, 2]) == dst
    # Since we are only copying 2 characters over, the null doesn't get sent over and therefore get
    # some of the original string in the copy.
    assert context.read_data(dst) == b"wollo!!!"
    for encoding in ["utf-16-le", "utf-16-be"]:
        context = ProcessorContext.from_arch()
        context.memory.write(src, u"world".encode(encoding))
        context.memory.write(dst, u"hello!!!".encode(encoding))
        assert builtin_funcs.strncpy(context, "wcsncpy", [dst, src, 2]) == dst
        assert context.read_data(dst, data_type=function_tracing.WIDE_STRING) == u"wollo!!!".encode(encoding)

    # test strdup/strndup
    heap_ptr = context.memory.HEAP_BASE
    context = ProcessorContext.from_arch()
    context.memory.write(src, b"hello")
    # should return a newly allocated string
    assert builtin_funcs.strdup(context, "strdup", [src]) == heap_ptr
    assert context.read_data(heap_ptr) == b"hello"
    context = ProcessorContext.from_arch()
    context.memory.write(src, b"hello")
    assert builtin_funcs.strndup(context, "strndup", [src, 2]) == heap_ptr
    assert context.read_data(heap_ptr) == b"he"

    # test strlen
    context = ProcessorContext.from_arch()
    context.memory.write(src, b"hello")
    assert builtin_funcs.strlen(context, "strlen", [src]) == 5
    for encoding in ["utf-16-le", "utf-16-be"]:
        context = ProcessorContext.from_arch()
        context.memory.write(src, u"hello".encode(encoding))
        assert builtin_funcs.strlen(context, "wcslen", [src]) == 5


@pytest.mark.in_ida
def test_function_signature():
    """Tests FunctionSignature object."""
    import idc
    from kordesii.utils import function_tracing
    from kordesii.utils import decoderutils

    xor_func_ea = 0x00401000
    tracer = function_tracing.get_tracer(xor_func_ea)

    # Basic tests.
    context = tracer.context_at(xor_func_ea)
    func_sig = context.get_function_signature(func_ea=xor_func_ea)
    assert func_sig.declaration == "_BYTE *__cdecl sub_401000(_BYTE *a1, char a2);"
    assert func_sig.arg_types == ("_BYTE * a1", "char a2")
    args = func_sig.args
    assert len(args) == 2
    assert args[0].name == "a1"
    assert args[0].type == "_BYTE *"
    assert args[0].value == 0
    assert args[1].name == "a2"
    assert args[1].type == "char"
    assert args[1].value == 0

    # Test that we can manipulate signature.
    func_sig.arg_types += ("int new_arg",)
    assert func_sig.declaration == "_BYTE *__cdecl sub_401000(_BYTE *a1, char a2, int new_arg);"
    args = func_sig.args
    assert len(args) == 3
    assert args[2].name == "new_arg"
    assert args[2].type == "int"
    assert args[2].value == 0

    # Now test using iter_function_args

    # First force an incorrect number of arguments.
    idc.SetType(xor_func_ea, " _BYTE *__cdecl sub_401000(_BYTE *a1)")
    func = decoderutils.SuperFunc_t(xor_func_ea)

    # Then test we can force 2 arguments anyway.
    results = []
    for ea in func.calls_to:
        tracer = function_tracing.get_tracer(ea)
        for context in tracer.iter_context_at(ea):
            # The function signature only gives 1 argument now.
            func_sig = context.get_function_signature()
            assert len(func_sig.args) == 1
            # But we force 2.
            args = context.get_function_args(num_args=2)
            assert len(args) == 2
            results.append(args)
    assert results == [
        [4243456, 1],
        [4243472, 2],
        [4243500, 3],
        [4243548, 4],
        [4243584, 5],
        [4243616, 6],
        [4243652, 19],
        [4243696, 23],
        [4243732, 26],
        [4243744, 35],
        [4243760, 39],
        [4243768, 64],
        [4243776, 70],
        [4243804, 115],
        [4243828, 117],
        [4243868, 119],
        [4243908, 122],
        [4243960, 127],
    ]

    # Test that we can force function signatures.
    with pytest.raises(RuntimeError):
        context.get_function_args(0xFFF)
    with pytest.raises(RuntimeError):
        context.get_function_signature(0xFFF)
    assert len(context.get_function_args(0xFFF, num_args=3)) == 3
    func_sig = context.get_function_signature(0xFFF, force=3)
    assert func_sig.declaration == "int __cdecl no_name();"

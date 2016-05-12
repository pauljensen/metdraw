import build as Build
import boundary as Bnd
import os

def metdraw(sbml_filename):
    cfilelist = []
    model = Build.makeModel(sbml_filename)

    # Adds comp c to cfilelist in a manner implemented like a postfix
    # calculator. If the level of c is less than the comp before it, the
    # previous two comps are popped off the stack, combined and pushed,
    # then c is pushed. If the level of c is the same as the level of the
    # comp on top of the stack, the top comp is popped and aligned with c,
    # then pushed. Else, c is pushed to the stack.
    def addTo(c):
        l = len(cfilelist)
        if l == 0:
            cfilelist.append(c)
        else:
            c2 = cfilelist[l-1]
            if c[1] > c2[1]:
                cfilelist.append(c)
            elif c[1] == c2[1]:
                x = cfilelist.pop()
                cfilelist.append((Bnd.combineSVGs(x[0],c[0],
                                                  align=True), x[1]))
                os.remove(c[0])
            else:
                c2 = cfilelist.pop()
                c3 = cfilelist.pop()
                Bnd.bounding_box(c2[0])
                cfilelist.append((Bnd.combineSVGs(c3[0],c2[0]), c3[1]))
                os.remove(c2[0])
                cfilelist.append(c)

    # Recursively add comps to cfilelist using pre-order traversal.
    # Level is a measure of how many comps a given comp is nested within
    def allc(model, level):
        if model ==[]:
            return
        for c in model.compartments:
            x = Build.drawCompartment(sbml_filename, c)
            addTo((x, level))
            allc(c, (level+1))

    # In the case where "addTo()" was not enough to completely render
    # the model, "combineAll()" will recursively go through the rest
    # of the comps, adding them together in a level-specific way. It
    # scans the list until two comps are found that can be combined,
    # then combines them and pushes it back to the top of the list.
    def combineAll(filelist):
        if filelist == []:
            return
        if len(filelist) == 1:
            return Bnd.bounding_box(filelist[0][0])
        if len(filelist) == 2:
            x1 = filelist.pop()
            x2 = filelist.pop()
            Bnd.bounding_box(x1[0])
            filelist.append((Bnd.combineSVGs(x2[0],x1[0]), x2[1]))
            os.remove(x1[0])
            return combineAll(filelist)
        else:
            count = 1
            l = len(filelist)
            curr = filelist[0]
            nxt = filelist[1]
            while curr[1] < nxt[1] and count < l-1:
                curr = nxt
                nxt = filelist[count+1]
                count += 1
            if curr[1] >= nxt[1]:
                x1 = filelist.pop(count-2)
                x2 = filelist.pop(count-2)
                if curr[1] == nxt[1]:
                    filelist.insert(count-2,
                                    ((Bnd.combineSVGs(x1[0], x2[0],
                                                      align=True), x1[1])))
                    os.remove(x2[0])
                    combineAll(filelist)
                else:
                    Bnd.bounding_box(x1[0])
                    filelist.insert(count-2,
                                    ((Bnd.combineSVGs(x1[0], x2[0])), x1[1]))
                    os.remove(x2[0])
                    combineAll(filelist)
            else:
                x1 = filelist.pop(count-1)
                x2 = filelist.pop(count-1)
                Bnd.bounding_box(x2[0])
                filelist.insert(count-1,
                                ((Bnd.combineSVGs(x1[0], x2[0])), x1[1]))
                os.remove(x2[0])
                combineAll(filelist)

    allc(model, 0)
    combineAll(cfilelist)

metdraw("xmltest.xml")